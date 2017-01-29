$(function () {
    "use strict";

    var $add_form_btn = $("#add_another_form_btn");
    var $total_forms_element = $("#id_sportregistrations-TOTAL_FORMS");

    var max_num_forms = parseInt($("#id_sportregistrations-MAX_NUM_FORMS").val());
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
        // Want to get all sport registration forms after the form that was removed.
        var $optionalSportRegForms = $removedForm.nextAll("div.multiField");
        if ($optionalSportRegForms.length === 0) {
            $optionalSportRegForms = $("#additional_forms").find("div.multiField");
        }
        $optionalSportRegForms.each(function (index, formElem) {
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
    };

    toggleAddFormBtnDisabled();


    $add_form_btn.click(function (e) {
        e.preventDefault();
        e.stopPropagation();
        var new_form_num = getTotalNumForms();
        if (new_form_num <= max_num_forms) {
            var form_data = $("#empty_form").html();
            form_data = form_data.replace(/__prefix__/g, new_form_num);
            form_data = form_data.replace(/data-form-num="-?\d*"/, "data-form-num=\"" + new_form_num + "\"");
            var trashIcon = '<span data-toggle="tooltip" data-placement="top" title="Remove form" class="fa fa-trash trash-delete pull-right"></span>';
            $("<div class='multiField'>" + trashIcon + form_data + "</div>").hide().appendTo($("#additional_forms")).fadeIn(800);
            window.scrollTo(0, document.body.scrollHeight);
            incrementTotalForms();
            toggleAddFormBtnDisabled();
            $('[data-toggle="tooltip"]').tooltip();
        }
        return false;
    });


    $(document).on("click", ".fa-trash.trash-delete", function (e) {
        $(this).parent().fadeOut(300, function () {
            decrementTotalForms();
            toggleAddFormBtnDisabled();
            fixFormNumbers($(this));
            $(this).remove();
        });
    });

});
