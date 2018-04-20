/* eslint-disable jsx-a11y/click-events-have-key-events */
/* eslint-disable jsx-a11y/anchor-is-valid */
import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

import { playerPropType } from '../common/proptypes';
import TooltipComponent from '../common/TooltipComponent';


const PlayerComponent = (props) => {
  const {
    player,
    canUpdate,
    handleRemovePlayer,
  } = props;
  const { user } = player;

  return (
    <div className={classNames('list-group-item text-left animated fadeIn', { disabled: !canUpdate })}>
      <span>{`#${player.jersey_number} ${user.first_name} ${user.last_name} ${player.position}`}</span>
      {canUpdate &&
      <span className="pull-right">
        <TooltipComponent placement="left" title="Remove player">
          <a tabIndex="0" role="button" onClick={() => handleRemovePlayer(player)}>
            <i className="fa fa-trash fa-trash-red" />
          </a>
        </TooltipComponent>
      </span>
      }
    </div>
  );
};

PlayerComponent.propTypes = {
  player: playerPropType.isRequired,
  canUpdate: PropTypes.bool.isRequired,
  handleRemovePlayer: PropTypes.func.isRequired,
};

export default PlayerComponent;
