$(function () {
  "use strict";

  $('[data-toggle="tooltip"]').tooltip();

  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      var cookies = document.cookie.split(";");
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + "=")) {
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
      dropupAuto: true,
      template: {
        caret: '<span class="fa fa-caret-down"></span>'
      }
    };
    $.extend(options, option_overrides);
    this.selectpicker(options);
    return this;
  };

  $.fn.enableDatetimepicker = function (option_overrides) {
    var options = {
      format: 'MM/DD/YYYY hh:mm A',
      useCurrent: false,
      useStrict: true,
      showClose: true,
      allowInputToggle: true,
      icons: {
        time: 'fa fa-clock-o',
        date: 'fa fa-calendar',
        up: 'fa fa-caret-up',
        down: 'fa fa-caret-down',
        previous: 'fa fa-caret-left',
        next: 'fa fa-caret-right',
        today: 'glyphicon glyphicon-screenshot',
        clear: 'fa fa-trash',
        close: 'fa fa-times'
      }
    };
    $.extend(options, option_overrides);
    this.datetimepicker(options);
    return this;
  };

  $("#edit_account_link.disabled").click(function (e) {
    e.preventDefault();
    e.stopPropagation();
    return false;
  });

  $("#logout_btn_acct_menu").click(function (e) {
    e.preventDefault();
    e.stopPropagation();
    $("#logout_form").submit();
    return false;
  });

  $(".js-btn-back").click(function (e) {
    e.preventDefault();
    e.stopPropagation();
    history.back();
  });

  var hasLocalStorage = function () {
    try {
      var item = 'test';
      localStorage.setItem(item, item);
      localStorage.removeItem(item);
      return true;
    } catch (e) {
      return false;
    }
  };

  var setLocalStorageItem = function (key, value) {
    if (!hasLocalStorage()) {
      return;
    }
    localStorage.setItem(key, value);
  };

  var getLocalStorageItem = function (key) {
    return hasLocalStorage() ? localStorage.getItem(key) : null;
  };

  var computePersistentTabKey = function () {
    var pathname = window.location.pathname;
    // Convert '/' to '-', omitting the root '/'. This assumes there is a trailing '/'.
    var key = pathname.substr(1).replace(/\//g, '-');
    return key.concat('active-tab');
  };

  $("a[data-toggle='tab']").on('shown.bs.tab', function (e) {
    var key = computePersistentTabKey();
    var targetId = $(e.target).attr('id');
    setLocalStorageItem(key, '#' + targetId);
  });

  var key = computePersistentTabKey();
  var elementId = getLocalStorageItem(key);
  if (elementId !== null) {
    $(elementId).tab('show');
  }
});
