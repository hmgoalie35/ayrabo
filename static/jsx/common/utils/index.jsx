import Noty from 'noty';


export const showAPIErrorMessage = () => {
  $('.js-api-error').animateCss('fadeIn').removeClass('hidden');
};

export const isMobileDevice = () => /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase());

/**
 * Creates a noty notification but does not show it. Remember to call `.show`.
 * @param text Notification text
 * @param type Notification type. Choices are the same as django. success, info, warning, danger
 * @returns {Noty}
 */
export const createNotification = (text, type) => {
  const timeout = text.length >= 100 ? 6000 : 4000;
  const layout = isMobileDevice() ? 'top' : 'topRight';
  const openAnimation = isMobileDevice() ? 'bounceInDown' : 'bounceInRight';
  const closeAnimation = isMobileDevice() ? 'bounceOutUp' : 'bounceOutRight';
  return new Noty({
    theme: 'relax',
    text,
    type,
    layout,
    timeout,
    force: true,
    closeWith: ['click', 'button'],
    progressBar: true,
    animation: {
      open: `animated ${openAnimation}`,
      close: `animated ${closeAnimation}`,
      easing: 'swing',
      speed: 500,
    },
  });
};

export const pluralize = (text, count, suffix = 's') => (count === 1 ? text : `${text}${suffix}`);
