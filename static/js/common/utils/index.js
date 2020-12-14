import Noty from 'noty';

/**
 * Toggle the api error banner
 * @param state The state to toggle the error banner to. Choose from `show` or `hide`
 */
export const toggleAPIErrorMessage = (state, message = '') => {
  let animateClass = null;
  // true means class is added, false means class is removed
  let classState = null;
  if (state === 'show') {
    animateClass = 'fadeIn';
    classState = false;
  } else if (state === 'hide') {
    animateClass = 'fadeOut';
    classState = true;
  }

  if (message) $('.js-api-error-text').html(message);
  $('.js-api-error').animateCss(animateClass).toggleClass('hidden', classState);
};


export const handleAPIError = (jqXHR) => {
  // This may be null if a 500 error occurs (html is returned instead of json and we'd want to use
  // responseText). I'd rather not log the html to the console even though it's still visible in
  // the network tab.
  const error = jqXHR.responseJSON;
  // This isn't really doing much since ajax errors already get logged to the console. This hook
  // is mainly here for when we eventually push to sentry
  console.error(jqXHR.status, error);
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

export const redirect = to => window.location.replace(to);

export const navigate = to => window.location.assign(to);

export const reload = () => window.location.reload();
