function getQueryVariable(variable) {
	var query = window.location.search.substring(1);
	var vars = query.split("&");
	for (var i=0;i<vars.length;i++) {
		var pair = vars[i].split("=");
		if(pair[0] == variable){return pair[1];}
	}
	return(false);
}


jQuery( document ).ready(function( $ ) {
	$('#html h1').addClass('prettify');

	window.jsprettify.run();

	$('.topic h2').click( function(){
		$theSwiper = $(this).parent().children('.swiper-container');
		// this element is already active, so let's deactivate it
		if ( $(this).parent().hasClass('active') ) {
			$theSwiper.swiper().destroy();
			$theSwiper.children('.arrow-left').off();
			$theSwiper.children('.arrow-right').off();
			$theSwiper.children('.pagination').empty();
			$('div.active').removeClass('active');
		}
		// this element is NOT active, so let's activate it
		else {
			// first, deactivate any other currently-active element
			$alreadyActive = $('div.active').children('.swiper-container');
			if ( $alreadyActive.length > 0 ) {
				$alreadyActive.swiper().destroy();
				$alreadyActive.children('.arrow-left').off();
				$alreadyActive.children('.arrow-right').off();
				$alreadyActive.children('.pagination').empty();
				$alreadyActive.parent().removeClass('active');
			}
			// now activate this element
			$(this).parent().addClass('active');
			// create swiper object
			var mySwiper = $theSwiper.swiper({
				pagination: $theSwiper.find('.pagination')[0],
				createPagination: true,
				paginationClickable: true
			});
			// add nav arrows
			$theSwiper.children('.arrow-left').click(function(e){ mySwiper.swipePrev() });
			$theSwiper.children('.arrow-right').click(function(e){ mySwiper.swipeNext() });
			// scroll to the element we just clicked, in case we got knocked out of whack		
			$( document ).scrollTo( $(this), 800 );
		}
	});
});