import { configure } from 'enzyme/build';
import $ from 'jquery';
import Adapter from 'enzyme-adapter-react-16/build';

// Setup enzyme
configure({ adapter: new Adapter() });

global.$ = $;
global.jQuery = $;
