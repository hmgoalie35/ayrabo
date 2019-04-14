import { configure } from 'enzyme';
import $ from 'jquery';
import Adapter from 'enzyme-adapter-react-16';

// Setup enzyme
configure({ adapter: new Adapter() });

global.$ = $;
global.jQuery = $;
