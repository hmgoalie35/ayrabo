$(function () {
    "use strict";
    $("#logout_btn_acct_menu").click(function (e) {
        e.preventDefault();
        e.stopPropagation();
        $("#logout_form").submit();
        return false;
    });
});
