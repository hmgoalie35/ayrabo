/* eslint-disable import/prefer-default-export */
import { createNotification as _createNotification } from '../common/utils';

import '../../scss/main.scss';

import 'bootstrap-sass/assets/javascripts/bootstrap.min';
import '../jQueryCommon';


export const createNotification = (msg, level) => _createNotification(msg, level);
