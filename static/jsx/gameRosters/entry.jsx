/* eslint-disable import/prefer-default-export */
import { render } from 'react-dom';

import GameRostersUpdateComponent from './GameRostersUpdateComponent';
import { withErrorHandling } from '../common/ErrorHandler';


export const initGameRostersUpdateComponent = opts =>
  render(
    withErrorHandling(GameRostersUpdateComponent, opts),
    document.getElementById(opts.container),
  );
