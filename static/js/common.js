$(function () {
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

  var csrftoken = getCookie('csrftoken');

  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }

  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader('X-CSRFToken', csrftoken);
      }
    }
  });

  var isMobileDevice = function () {
    return (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase()));
  };

  $.fn.enableBootstrapSelect = function (option_overrides) {
    var options = {
      header: 'Select an option',
      iconBase: 'fa',
      tickIcon: 'fa-check',
      showTick: true,
      liveSearch: true,
      liveSearchNormalize: true,
      liveSearchPlaceholder: 'Search',
      noneSelectedText: '---------',
      selectedTextFormat: 'count > 2',
      mobile: isMobileDevice(),
      dropupAuto: true,
      template: {
        caret: '<span class="fa fa-caret-down"></span>'
      }
    };
    $.extend(true, options, option_overrides);
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
    $.extend(true, options, option_overrides);
    this.datetimepicker(options);
    return this;
  };

  $.fn.enableDataTable = function (option_overrides) {
    // Some attributes that should be specified: `dom`, `order`.
    var options = {
      pageLength: 10,
      language: {
        paginate: {
          previous: '<i class="fa fa-angle-double-left"></i>',
          next: '<i class="fa fa-angle-double-right"></i>',
        },
        search: '',
        searchPlaceholder: 'Search items',
        zeroRecords: 'No items match your search criteria.',
      }
    };
    $.extend(true, options, option_overrides);
    this.DataTable(options);
    return this;
  };

  $.fn.extend({
    animateCss: function (animationName, callback) {
      var animationEnd = (function (el) {
        var animations = {
          animation: 'animationend',
          OAnimation: 'oAnimationEnd',
          MozAnimation: 'mozAnimationEnd',
          WebkitAnimation: 'webkitAnimationEnd',
        };

        for (var t in animations) {
          if (el.style[t] !== undefined) {
            return animations[t];
          }
        }
      })(document.createElement('div'));

      this.addClass('animated ' + animationName).one(animationEnd, function () {
        $(this).removeClass('animated ' + animationName);

        if (typeof callback === 'function') callback();
      });

      return this;
    },
  });

  $('#edit_account_link.disabled').click(function (e) {
    e.preventDefault();
    e.stopPropagation();
    return false;
  });

  $('#logout_btn_acct_menu').click(function (e) {
    e.preventDefault();
    e.stopPropagation();
    $('#logout_form').submit();
    return false;
  });

  $('.js-btn-back').click(function (e) {
    e.preventDefault();
    e.stopPropagation();
    history.back();
  });

  // Any tabs on the site can opt into this functionality by adding `data-tab=<value>`.
  // The corresponding Django view needs to set the `active` class based off of the `tab` query param.
  $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
    var tab = $(e.target).data('tab');
    if (tab) {
      var baseUrl = window.location.origin + window.location.pathname;
      window.history.replaceState({}, '', baseUrl + '?tab=' + encodeURIComponent(tab));
    }
  });
});
