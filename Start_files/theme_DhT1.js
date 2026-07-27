/* Copyright (C) YOOtheme GmbH, http://www.gnu.org/licenses/gpl.html GNU/GPL */

jQuery(function($) {

    var config = $('html').data('config') || {};

    // Social buttons
    $('article[data-permalink]').socialButtons(config);
	
	// Special for 100% height
	$(window).load(function() {
           $("#jp-left").height($(document).height());
           $("#jp-right").height($(document).height());
     });
});

