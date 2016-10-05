$(function () {
    "use strict";

    $('[data-toggle="tooltip"]').tooltip();

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie("csrftoken");

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $.isMobileDevice = function () {
        return (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase()));
    };

    $.fn.enableSelect2 = function (user_options) {
        var defaults = {
            theme: "bootstrap"
            // placeholder: placeholder,
            // allowClear: true
        };

        var options = $.extend(defaults, user_options);

        // Show browser's default select box when on mobile
        if (!$.isMobileDevice()) {
            this.select2(options);
        }
        return this;
    };
});
