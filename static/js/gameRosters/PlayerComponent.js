/* eslint-disable jsx-a11y/click-events-have-key-events */
/* eslint-disable jsx-a11y/anchor-is-valid */
import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

import { playerPropType } from '../common/proptypes';
import TooltipComponent from '../common/TooltipComponent';


class PlayerComponent extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      isStarterHovered: false,
    };
  }

  render() {
    const {
      player,
      canUpdate,
      handleToggleStartingGoalie,
      handleRemovePlayer,
    } = this.props;
    const { isStarterHovered } = this.state;
    const { user } = player;

    let starterEl;
    if (player.position === 'G') {
      if (!player.is_starting) {
        starterEl = (
          <a
            role="button"
            className="mr12 label label-default set-starter-label no-outline"
            tabIndex="0"
            onClick={() => handleToggleStartingGoalie(player, true)}
          >
            Set as Starter
          </a>
        );
      } else {
        starterEl = (
          <a
            role="button"
            className={`mr12 label clickable no-outline ${isStarterHovered ? 'label-danger' : 'label-info'}`}
            tabIndex="0"
            onMouseEnter={() => this.setState({ isStarterHovered: true })}
            onMouseLeave={() => this.setState({ isStarterHovered: false })}
            onClick={() => handleToggleStartingGoalie(player, false)}
          >
            {isStarterHovered ? 'Remove Starter' : 'Starter'}
          </a>
        );
      }
    }

    return (
      <div className={classNames('list-group-item animated fadeIn flex flex-align-center flex-justify-space-between', { disabled: !canUpdate })}>
        <span>{`#${player.jersey_number} ${user.first_name} ${user.last_name} ${player.position}`}</span>
        {canUpdate &&
          <div className="flex flex-align-center">
            {starterEl}
            <TooltipComponent placement="left" title="Remove player">
              <a tabIndex="0" role="button" onClick={() => handleRemovePlayer(player)}>
                <i className="fa fa-trash fa-trash-red" />
              </a>
            </TooltipComponent>
          </div>
        }
      </div>
    );
  }
}

PlayerComponent.propTypes = {
  player: playerPropType.isRequired,
  canUpdate: PropTypes.bool.isRequired,
  handleRemovePlayer: PropTypes.func.isRequired,
  handleToggleStartingGoalie: PropTypes.func.isRequired,
};

export default PlayerComponent;
