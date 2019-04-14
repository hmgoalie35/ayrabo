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
    'operator-linebreak': 'off',
    // React
    'react/jsx-wrap-multilines': 'off',
    'react/jsx-one-expression-per-line': 'off',
    'react/jsx-filename-extension': 'off',
    // Import
    'import/no-extraneous-dependencies': 'off',
  },
};
