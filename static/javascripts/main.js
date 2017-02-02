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

    var isMobileDevice = function () {
        return (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase()));
    };

    $.fn.enableBootstrapSelect = function (option_overrides) {
        var options = {
            header: "Select an option",
            iconBase: "fa",
            tickIcon: "fa-check",
            showTick: true,
            liveSearch: true,
            liveSearchNormalize: true,
            liveSearchPlaceholder: "Search",
            noneSelectedText: "---------",
            selectedTextFormat: "count > 2",
            mobile: isMobileDevice(),
            dropupAuto: true
        };

        $.extend(options, option_overrides);
        this.selectpicker(options);

        return this;
    };

    $("#edit_account_link.disabled").click(function (e) {
        e.preventDefault();
        e.stopPropagation();
        return false;
    });
});
