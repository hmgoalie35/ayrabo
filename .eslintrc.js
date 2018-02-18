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
    'comma-dangle': ['error', {
      arrays: 'always-multiline',
      objects: 'always-multiline',
      imports: 'always-multiline',
      exports: 'always-multiline',
      functions: 'only-multiline',
    }],
    // React
    'react/jsx-wrap-multilines': 'off',
    // Import
    'import/no-extraneous-dependencies': 'off',
  },
};
