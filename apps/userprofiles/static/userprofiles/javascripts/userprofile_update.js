$(function () {
    "use strict";

    $("#id_language").enableBootstrapSelect({header: "Select a language"});
    $("#id_timezone").enableBootstrapSelect({header: "Select a timezone"});

    $(".more-sport-info").click(function () {
        var $elem = $(this).find("span.more-sport-info-fa-caret");
        $elem.toggleClass("fa-caret-down fa-caret-up");
    });

    // allows click-through of edit registration links
    $("[name=edit_registration_link]").click(function (event) {
        event.preventDefault();
        event.stopPropagation();
        window.location.href = $(this).attr('href');
        return false;
    });

    $("#revoke_token_form").submit(function (event) {
        event.preventDefault();
        event.stopPropagation();
        var promise = $.ajax({
            url: $(this).attr("action"),
            method: 'DELETE'
        });
        var onSuccess = function (data, textStatus, jqXHR) {
            window.location.reload(true);
        };

        var onFailure = function (data, textStatus, errorThrown) {
            alert("Error revoking api token: " + errorThrown + ", please try again in a few moments.");
        };

        promise.then(onSuccess, onFailure);
        return false;
    });

});
