import React from 'react';
import PropTypes from 'prop-types';

import PlayerComponent from './PlayerComponent';
import { playerPropType } from '../common/proptypes';
import Loading from '../common/Loading';


export default class GameRosterComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    const {
      team,
      players,
      canUpdate,
      teamType,
    } = this.props;

    let element;
    if (players === null) {
      element = (<div className="mt20"><Loading /></div>);
    } else if (players.length === 0) {
      element = (
        <div className="list-group-item">
          There are no players on this roster.
        </div>
      );
    } else {
      element = (
        players.map(player =>
          <PlayerComponent
            key={player.id}
            player={player}
            canUpdate={canUpdate}
          />)
      );
    }

    return (
      <div className="col-md-6 game-roster-component">
        <div className="text-center">
          <h4>{teamType} Team</h4>
          <div className="mb10"><strong>{team}</strong></div>
          <div className="list-group">
            {element}
          </div>
        </div>
      </div>
    );
  }
}

GameRosterComponent.propTypes = {
  team: PropTypes.string.isRequired,
  players: PropTypes.arrayOf(playerPropType),
  canUpdate: PropTypes.bool.isRequired,
  teamType: PropTypes.oneOf(['Home', 'Away']).isRequired,
};

GameRosterComponent.defaultProps = {
  players: null,
};
