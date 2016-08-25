$(function () {
    "use strict";
    $("[name='remove_role_btn']").click(function (event) {
        event.preventDefault();
        event.stopPropagation();

        var promise = $.ajax({
            url: $(this).attr("data-url"),
            method: "PATCH"
        });

        var onSuccess = function (data, textStatus, jqXHR) {
            window.location.reload(true);
        };

        var onFailure = function (data, textStatus, errorThrown) {
            console.error(textStatus, data.responseText);
        };

        promise.then(onSuccess, onFailure);

        return false;
    });
});
