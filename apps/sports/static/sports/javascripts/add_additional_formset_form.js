$(function () {
    "use strict";

    var $add_form_btn = $("#add_another_form_btn");

    var $total_forms_element = $("#id_sportregistration_set-TOTAL_FORMS");
    var total_num_forms = parseInt($total_forms_element.val());
    var max_num_forms = parseInt($("#id_sportregistration_set-MAX_NUM_FORMS").val());
    if (total_num_forms === max_num_forms) {
        $add_form_btn.attr("disabled", "disabled").addClass("disabled");
    }

    $add_form_btn.click(function (event) {
        event.preventDefault();
        event.stopPropagation();
        var new_form_num = parseInt($total_forms_element.val());
        if (new_form_num <= max_num_forms) {
            var form_data = $("#empty_form").html();
            form_data = form_data.replace(/__prefix__/g, new_form_num);
            new_form_num += 1;
            $total_forms_element.val(new_form_num);
            $("<div class=multiField>" + form_data + "</div>").hide().appendTo($("#additional_forms")).fadeIn(800);
            window.scrollTo(0, document.body.scrollHeight);
            if (new_form_num === max_num_forms) {
                $(this).attr("disabled", "disabled").addClass("disabled");
            }
        }
        return false;
    });
});
