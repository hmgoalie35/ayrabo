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
    'arrow-parens': ['error', 'as-needed', { requireForBlockBody: true }],
    'no-multiple-empty-lines': 'off',
    // React
    'react/jsx-wrap-multilines': 'off',
    'react/jsx-one-expression-per-line': 'off',
    'react/jsx-filename-extension': 'off',
    'react/jsx-props-no-spreading': 'off',
    'react/jsx-fragments': ['error', 'element'],
    'react/jsx-curly-newline': 'off',
    // Import
    'import/no-extraneous-dependencies': 'off',
  },
};
