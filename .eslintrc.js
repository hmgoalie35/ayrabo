module.exports = {
  extends: 'airbnb',
  root: true,
  env: {
    browser: true,
    jquery: true,
    jest: true,
  },
  rules: {
    // Built in eslint
    'no-console': 'off',
    'class-methods-use-this': 'off',
    'function-paren-newline': 'off',
    // React
    'react/jsx-wrap-multilines': 'off',
    // Import
    'import/no-extraneous-dependencies': 'off',
  },
};
