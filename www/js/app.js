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
		$(this).parent().toggleClass('active');
		$theSwiper = $(this).parent().children('.swiper-container');
		if ( $(this).parent().hasClass('active') ) {
			var mySwiper = $theSwiper.swiper({
				pagination: $theSwiper.find('.pagination')[0],
				createPagination: true,
				paginationClickable: true
			});
			$theSwiper.children('.arrow-left').click(function(e){ mySwiper.swipePrev() });
			$theSwiper.children('.arrow-right').click(function(e){ mySwiper.swipeNext() });
			// console.log( $theSwiper );

		}
		else {
			console.log('INACTIVE!');
			$theSwiper.swiper().destroy();
			$theSwiper.children('.arrow-left').off();
			$theSwiper.children('.arrow-right').off();
			// console.log( $theSwiper );
		}
	});
});