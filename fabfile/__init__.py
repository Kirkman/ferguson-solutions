#!/usr/bin/env python

import os

from fabric.api import local, require, settings, task
from fabric.state import env
from termcolor import colored

import app_config

# Other fabfiles
import assets
import data
import issues
import render
import text
import utils

if app_config.DEPLOY_TO_SERVERS:
    import servers

if app_config.DEPLOY_CRONTAB:
    import cron_jobs

# Bootstrap can only be run once, then it's disabled
if app_config.PROJECT_SLUG == '$NEW_PROJECT_SLUG':
    import bootstrap

"""
Base configuration
"""
env.user = app_config.SERVER_USER
env.forward_agent = True

env.hosts = []
env.settings = None

"""
Environments

Changing environment requires a full-stack test.
An environment points to both a server and an S3
bucket.
"""
@task
def production():
    """
    Run as though on production.
    """
    env.settings = 'production'
    app_config.configure_targets(env.settings)
    env.hosts = app_config.SERVERS

@task
def staging():
    """
    Run as though on staging.
    """
    env.settings = 'staging'
    app_config.configure_targets(env.settings)
    env.hosts = app_config.SERVERS

"""
Branches

Changing branches requires deploying that branch to a host.
"""
@task
def stable():
    """
    Work on stable branch.
    """
    env.branch = 'stable'

@task
def master():
    """
    Work on development branch.
    """
    env.branch = 'master'

@task
def branch(branch_name):
    """
    Work on any specified branch.
    """
    env.branch = branch_name

@task
def tests():
    """
    Run Python unit tests.
    """
    local('nosetests')

"""
Deployment

Changes to deployment requires a full-stack test. Deployment
has two primary functions: Pushing flat files to S3 and deploying
code to a remote server if required.
"""

def _deploy_to_graphics():
    # -p creates any uncreated directories in the path. avoids errors.
    # -m ### creates the directories with whatever permission level you specify
    mkdir = ('ssh %s@%s mkdir -p -m 755 %s ') % (
        app_config.S3_USER,
        app_config.S3_BUCKET['bucket_name'],
        app_config.S3_BASE_URL # Base_URL doesn't include the "user@server:" part
    )
    local(mkdir)

    # -v verbose mode
    # -a stands for "archive" and syncs recursively and preserves symbolic links, special and device files, modification times, group, owner, and permissions.
    # -z compresses files for faster network transfer
    # -P combines the flags --progress and --partial. The first gives you a progress bar for transfers; the second allows you to resume interrupted transfers
    # --delete removes files on receiving side that don't exist on the sending side
    # --exclude lets you specify files/patterns you don't want to transfer
    sync = ('rsync -vaz --delete --exclude ".DS_Store" www/ %s ') % (
        app_config.S3_DEPLOY_URL # Deploy_URL DOES include the "user@server:" part, which we need for rsync
    )
    local(sync)

def _deploy_assets():
    """
    Deploy assets to S3.
    """

    sync_assets = 'rsync -a www/assets/ %s/assets/ --acl "public-read" --cache-control "max-age=%i" --region "%s"' % (
        app_config.S3_DEPLOY_URL,
        app_config.ASSETS_MAX_AGE,
        app_config.S3_BUCKET['region']
    )

    local(sync_assets)

def _gzip(in_path='www', out_path='.gzip'):
    """
    Gzips everything in www and puts it all in gzip
    """
    local('python gzip_assets.py %s %s' % (in_path, out_path))

@task
def update():
    """
    Update all application data not in repository (copy, assets, etc).
    """
    text.update()
    assets.sync()
    data.update()

@task
def deploy(remote='origin'):
    """
    Deploy the latest app to S3 and, if configured, to our servers.
    """
    require('settings', provided_by=[production, staging])

    if app_config.DEPLOY_TO_SERVERS:
        require('branch', provided_by=[stable, master, branch])

        if (app_config.DEPLOYMENT_TARGET == 'production' and env.branch != 'stable'):
            utils.confirm(
                colored("You are trying to deploy the '%s' branch to production.\nYou should really only deploy a stable branch.\nDo you know what you're doing?" % env.branch, "red")
            )

        servers.checkout_latest(remote)

        servers.fabcast('text.update')
        servers.fabcast('assets.sync')
        servers.fabcast('data.update')

        if app_config.DEPLOY_CRONTAB:
            servers.install_crontab()

        if app_config.DEPLOY_SERVICES:
            servers.deploy_confs()

    # update()
    render.render_all()
    # _gzip('www', '.gzip')
    # _deploy_to_s3()
    # _deploy_assets()
    _deploy_to_graphics()

"""
Destruction

Changes to destruction require setup/deploy to a test host in order to test.
Destruction should remove all files related to the project from both a remote
host and S3.
"""

@task
def shiva_the_destroyer():
    """
    Deletes the app from s3
    """
    require('settings', provided_by=[production, staging])

    utils.confirm(
        colored("You are about to destroy everything deployed to %s for this project.\nDo you know what you're doing?')" % app_config.DEPLOYMENT_TARGET, "red")
    )

    with settings(warn_only=True):
        sync = 'aws s3 rm s3://%s/%s/ --recursive --region "%s"' % (
            app_config.S3_BUCKET['bucket_name'],
            app_config.PROJECT_SLUG,
            app_config.S3_BUCKET['region']
        ) 

        local(sync)

        if app_config.DEPLOY_TO_SERVERS:
            servers.delete_project()

            if app_config.DEPLOY_CRONTAB:
                servers.uninstall_crontab()

            if app_config.DEPLOY_SERVICES:
                servers.nuke_confs()

