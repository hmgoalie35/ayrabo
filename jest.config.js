module.exports = {
  moduleNameMapper: {
    '\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$':
      '<rootDir>/static/jsx/__mocks__/fileMock.jsx',
  },
  roots: ['<rootDir>/static/jsx/'],
  setupFiles: ['<rootDir>/static/jsx/setupTests.jsx'],
  testURL: 'http://localhost',
};
