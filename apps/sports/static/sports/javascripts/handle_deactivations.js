$(function () {
  "use strict";
  $("[name='deactivate_btn']").click(function (e) {
    e.preventDefault();
    e.stopPropagation();

    var onSuccess = function (data, textStatus, jqXHR) {
      window.location.reload(true);
    };

    var onFailure = function (data, textStatus, errorThrown) {
      console.error(textStatus, data.responseText);
    };

    $.ajax({
      url: $(this).attr("data-url"),
      method: "PATCH"
    })
    .done(onSuccess)
    .fail(onFailure);

    return false;
  });
});
