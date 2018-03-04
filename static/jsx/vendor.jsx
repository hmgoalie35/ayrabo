// Import commonly used libraries so webpack can move them into a separate chunk and prevent
// duplication of libraries. This prevents clients from re-downloading vendor code when we add new
// features, even though the actual vendor code (react, react-dom, etc) might not have changed.
import 'react';
import 'react-dom';
import 'noty';
import 'lodash/util';
import 'lodash/array';
import 'react-bootstrap-typeahead';
// Any vendor scss/css can be imported into this vendor scss file.
import '../scss/vendor.scss';
