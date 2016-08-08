$(function () {
    "use strict";

    $(".more-sport-info").click(function () {
        var $elem = $(this).find("span.more-sport-info-fa-icon");
        $elem.toggleClass("fa-caret-square-o-down");
        $elem.toggleClass("fa-caret-square-o-up");
    });

    // allows click-through of edit registration links
    $("[name=edit_registration_link]").click(function (event) {
        event.preventDefault();
        event.stopPropagation();
        window.location.href = $(this).attr('href');
    });
});
