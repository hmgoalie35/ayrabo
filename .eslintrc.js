module.exports = {
  extends: 'airbnb',
  root: true,
  env: {
    browser: true,
    jquery: true,
  },
  rules: {
    // Built in eslint
    'no-console': 'off',
    'class-methods-use-this': 'off',
    // React
    'react/jsx-wrap-multilines': 'off',
  },
};
