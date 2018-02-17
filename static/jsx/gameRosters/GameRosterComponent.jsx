import React from 'react';
import PropTypes from 'prop-types';
import { Typeahead } from 'react-bootstrap-typeahead';


import PlayerComponent from './PlayerComponent';
import { playerPropType } from '../common/proptypes';
import Loading from '../common/Loading';
import { pluralize } from '../common/utils';


export default class GameRosterComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
    this.getOptions = this.getOptions.bind(this);
    this.handleTypeaheadChange = this.handleTypeaheadChange.bind(this);
  }

  getOptions(selectedPlayers, allPlayers) {
    const ids = selectedPlayers.map(player => player.id);
    return allPlayers.filter(player => !ids.includes(player.id));
  }

  // The param for this function is an array
  handleTypeaheadChange(selected) {
    const { handleAddPlayer } = this.props;
    // See https://github.com/ericgio/react-bootstrap-typeahead/blob/master/docs/Methods.md#clear
    if (selected.length) {
      this.typeahead.getInstance().clear();
    }
    handleAddPlayer(selected);
  }

  render() {
    const {
      team,
      selectedPlayers,
      allPlayers,
      canUpdate,
      teamType,
      handleRemovePlayer,
    } = this.props;

    let element;
    if (selectedPlayers === null) {
      element = (<div className="mt20"><Loading /></div>);
    } else if (selectedPlayers.length === 0) {
      element = (
        <div className="list-group-item">
          There are no players on this roster.
        </div>
      );
    } else if (!canUpdate) {
      element = (
        <div className="list-group-item">
          This game roster is currently unavailable.
        </div>
      );
    } else {
      element = (
        <React.Fragment>
          {selectedPlayers.map(player =>
            <PlayerComponent
              key={player.id}
              player={player}
              canUpdate={canUpdate}
              handleRemovePlayer={handleRemovePlayer}
            />)
          }
          <div className="text-center mt5">
            {`${selectedPlayers.length} ${pluralize('player', selectedPlayers.length)}`}
          </div>
        </React.Fragment>
      );
    }

    return (
      <div className="col-md-6 game-roster-component">
        <div className="text-center">
          <h4>{teamType} Team</h4>
          <div className="mb10"><strong>{team}</strong></div>
          {(selectedPlayers !== null && allPlayers !== null) &&
          <div className="text-left mb10">
            <Typeahead
              multiple
              highlightOnlyResult
              selectHintOnEnter
              onChange={this.handleTypeaheadChange}
              options={this.getOptions(selectedPlayers, allPlayers)}
              disabled={!canUpdate}
              emptyLabel="No players found."
              placeholder="Search players by first name, last name or jersey number"
              paginationText="Display more players"
              ref={(typeahead) => {
                this.typeahead = typeahead;
              }}
            />
          </div>
          }
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
  selectedPlayers: PropTypes.arrayOf(playerPropType),
  allPlayers: PropTypes.arrayOf(playerPropType),
  canUpdate: PropTypes.bool.isRequired,
  teamType: PropTypes.oneOf(['Home', 'Away']).isRequired,
  handleAddPlayer: PropTypes.func.isRequired,
  handleRemovePlayer: PropTypes.func.isRequired,
};

GameRosterComponent.defaultProps = {
  selectedPlayers: null,
  allPlayers: null,
};
