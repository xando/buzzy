$(function() {

	var FRAGMENT_NAME = '#the-text';
	var content = $(FRAGMENT_NAME);

	$(document).pjax('a', FRAGMENT_NAME, {'fragment': FRAGMENT_NAME});

	if (window.location.pathname.length > 1) {
		$.pjax({
			url: window.location.pathname,
			container: FRAGMENT_NAME,
			fragment: FRAGMENT_NAME
		});
	}
});
