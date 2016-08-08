$(function () {
    $(".more-sport-info").click(function () {
        var $elem = $(this).find("span.more-sport-info-fa-icon");
        $elem.toggleClass("fa-caret-square-o-down");
        $elem.toggleClass("fa-caret-square-o-up");
    });
});
