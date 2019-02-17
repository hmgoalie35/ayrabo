$(function () {
  $('[data-toggle="tooltip"]').tooltip();

  function updateTooltipTitle($element, title) {
    return $element.attr('title', title).tooltip('fixTitle').tooltip('show');
  }

  var clipboard = new ClipboardJS('.js-clipboard-btn');
  clipboard.on('success', function (e) {
    var $element = $(e.trigger);
    updateTooltipTitle($element, 'Copied!');
    setTimeout(function () {
      updateTooltipTitle($element, 'Copy');
      $element.blur();
    }, 2000);
    e.clearSelection();
  });

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

  $.fn.selectpicker.Constructor.BootstrapVersion = '3';
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
        search: '<i class="fa fa-search"></i>_INPUT_',
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
  $('a[data-toggle="tab"], a[data-toggle="pill"]').on('shown.bs.tab', function (e) {
    var tab = $(e.target).data('tab');
    if (tab) {
      var baseUrl = window.location.origin + window.location.pathname;
      window.history.replaceState({}, '', baseUrl + '?tab=' + encodeURIComponent(tab));
    }
  });

  // Turns a dropdown into a dropup if there is not enough space under the dropdown
  $(document).on('shown.bs.dropdown', '.dropdown', function () {
    // calculate the required sizes, spaces
    var $ul = $(this).children('.dropdown-menu');
    var $button = $(this).children('.dropdown-toggle');
    var ulOffset = $ul.offset();
    // how much space would be left on the top if the dropdown opened that direction
    var spaceUp = (ulOffset.top - $button.height() - $ul.height()) - $(window).scrollTop();
    // how much space is left at the bottom
    var spaceDown = $(window).scrollTop() + $(window).height() - (ulOffset.top + $ul.height());
    // switch to dropup only if there is no space at the bottom AND there is space at the top, or there isn't either but it would be still better fit
    if (spaceDown < 0 && (spaceUp >= 0 || spaceUp > spaceDown)) {
      $(this).addClass('dropup');
    }
  });

  $(document).on('hidden.bs.dropdown', '.dropdown', function () {
    // always reset after close
    $(this).removeClass('dropup');
  });

  $('.js-api-error-button').click(function (e) {
    e.preventDefault();
    e.stopPropagation();
    var $errorContainer = $('.js-api-error');
    $errorContainer.animateCss('fadeOut', function () {
      $errorContainer.addClass('hidden');
    });
    return false;
  });
});
