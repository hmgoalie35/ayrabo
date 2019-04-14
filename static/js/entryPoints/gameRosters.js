/* eslint-disable import/prefer-default-export */
import { render } from 'react-dom';
import { withErrorHandling } from '../common/ErrorHandler';

import GameRostersUpdateComponent from '../gameRosters/GameRostersUpdateComponent';


export const initGameRostersUpdateComponent = opts => (
  render(
    withErrorHandling(GameRostersUpdateComponent, opts),
    document.getElementById(opts.container),
  )
);
