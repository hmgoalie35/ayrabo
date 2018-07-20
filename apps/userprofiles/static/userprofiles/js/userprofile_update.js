$(function () {
  'use strict';

  $('#id_language').enableBootstrapSelect({ header: 'Select a language' });
  $('#id_timezone').enableBootstrapSelect({ header: 'Select a timezone' });

  $('.js-list-item-sport').click(function () {
    var $elem = $(this).find('.js-toggle-caret');
    $elem.toggleClass('fa-caret-down fa-caret-up');
  });
});
