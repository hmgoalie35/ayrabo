$(function () {
  "use strict";

  var prefix = $("#prefix").attr("data-prefix");
  var $add_form_btn = $("#add_another_form_btn");
  var $total_forms_element = $("#id_" + prefix + "-TOTAL_FORMS");

  var max_num_forms = parseInt($("#id_" + prefix + "-MAX_NUM_FORMS").val());
  var regex = /-\d+-/;


  var getTotalNumForms = function () {
    return parseInt($total_forms_element.val());
  };

  var toggleAddFormBtnDisabled = function () {
    var num_forms = getTotalNumForms();
    if (num_forms === max_num_forms) {
      $add_form_btn.attr("disabled", "disabled").addClass("disabled");
    } else {
      $add_form_btn.removeAttr("disabled").removeClass("disabled");
    }
  };

  var incrementTotalForms = function () {
    $total_forms_element.val(getTotalNumForms() + 1);
  };

  var decrementTotalForms = function () {
    $total_forms_element.val(getTotalNumForms() - 1);
  };

  var replaceAttrValues = function ($element, formNum) {
    var attrs = ["for", "id", "name"];
    $.each(attrs, function (index, attr) {
      var attrVal = $element.attr(attr);
      if (attrVal) {
        $element.attr(attr, attrVal.replace(regex, "-" + formNum + "-"));
      }
    });
  };

  var fixFormNumbers = function ($removedForm) {
    var formNum = $removedForm.find("[data-form-num]").data("form-num");
    var maxForms = getTotalNumForms();
    if (formNum === maxForms) {
      return;
    }
    // Want to get all forms after the form that was removed.
    var $optionalForms = $removedForm.nextAll("div.multiField");
    if ($optionalForms.length === 0) {
      var $forms = $("#additional_forms").find("div.multiField");
      // Exclude the form that was just removed (it is selected by the selector above)
      $optionalForms = $.map($forms, function (element, index) {
        var formNumOfElement = parseInt($(element).find("input[data-form-num]").data("form-num"));
        if (formNumOfElement !== formNum) {
          return element;
        }
      });
    }

    if ($optionalForms.length > 0) {
      $.each($optionalForms, function (index, formElem) {
        // Find all id, name, for attrs of the current element and its descendants and change the value based on
        // `formNum`
        var $allChildren = $(formElem).find(":not('span')");
        $allChildren.each(function (index, element) {
          replaceAttrValues($(element), formNum);
        });
        $(formElem).find("[data-form-num]").attr("data-form-num", formNum);
        formNum += 1;
        if (formNum > maxForms) {
          throw "Form number exceeded max num forms";
        }
      });
    }
  };

  var enableBootstrapSelect = function () {
    var type = $("#role_type").data("text") === 'referee' ? 'league' : 'team';
    var $selects = $("select[id$=-" + type + "]").filter(function (index, element) {
      var elementId = $(element).attr('id');
      return !elementId.includes("-__prefix__-");
    });
    $($selects).enableBootstrapSelect({ header: 'Select a ' + type });
  };

  toggleAddFormBtnDisabled();
  enableBootstrapSelect();


  $add_form_btn.click(function (e) {
    e.preventDefault();
    e.stopPropagation();
    var new_form_num = getTotalNumForms();
    if (new_form_num <= max_num_forms) {
      var form_data = $("#empty_form").html();
      form_data = form_data.replace(/__prefix__/g, new_form_num);
      form_data = form_data.replace(/data-form-num="-?\d*"/, "data-form-num=\"" + new_form_num + "\"");
      var trashIcon = '<span data-toggle="tooltip" data-placement="top" title="Remove form" class="fa fa-trash fa-trash-red pull-right"></span>';
      $("<div class='multiField'>" + trashIcon + form_data + "</div>").hide().appendTo($("#additional_forms")).fadeIn(800);
      window.scrollTo(0, document.body.scrollHeight);
      incrementTotalForms();
      toggleAddFormBtnDisabled();
      $('[data-toggle="tooltip"]').tooltip();
      enableBootstrapSelect();
    }
    return false;
  });


  $(document).on("click", ".fa-trash.fa-trash-red", function (e) {
    $(this).parent().fadeOut(300, function () {
      decrementTotalForms();
      toggleAddFormBtnDisabled();
      fixFormNumbers($(this));
      $(this).remove();
      enableBootstrapSelect();
    });
  });

});
