import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

import { playerPropType } from '../common/proptypes';
import TooltipComponent from '../common/TooltipComponent';


const PlayerComponent = ({ player, canUpdate }) => {
  const { user } = player;

  return (
    <div className={classNames('list-group-item text-left', { disabled: !canUpdate })}>
      <span>{`${user.first_name} ${user.last_name}`}</span>
      {canUpdate &&
      <span className="pull-right">
        <TooltipComponent placement="left" title="Remove player">
          <i className="fa fa-trash fa-trash-red" />
        </TooltipComponent>
      </span>
      }
    </div>
  );
};

PlayerComponent.propTypes = {
  player: playerPropType.isRequired,
  canUpdate: PropTypes.bool.isRequired,
};

export default PlayerComponent;
