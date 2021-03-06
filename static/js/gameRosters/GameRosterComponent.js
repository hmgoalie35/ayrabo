import React from 'react';
import PropTypes from 'prop-types';
import { Typeahead } from 'react-bootstrap-typeahead';
import { uniqueId } from 'lodash';

import PlayerComponent from './PlayerComponent';
import { playerPropType } from '../common/proptypes';
import Loading from '../common/Loading';
import { handleAPIError, pluralize } from '../common/utils';
import SeasonRosterDropdownComponent from './SeasonRosterDropdownComponent';
import APIClient from '../common/APIClient';


export default class GameRosterComponent extends React.Component {
  constructor(props) {
    super(props);
    this.client = new APIClient();
    this.typeaheadId = uniqueId('typeahead_');
    this.state = {
      seasonRosters: null,
    };
    this.getOptions = this.getOptions.bind(this);
    this.handleTypeaheadChange = this.handleTypeaheadChange.bind(this);
    this.getSeasonRosters = this.getSeasonRosters.bind(this);
  }

  componentDidMount() {
    const { canUpdate } = this.props;
    if (canUpdate) {
      this.getSeasonRosters();
    }
  }

  getSeasonRosters() {
    const { teamId, seasonId } = this.props;
    this.client.get(
      `teams/${teamId}/season-rosters`,
      { season: seasonId }
    ).then(
      data => this.setState({ seasonRosters: data }),
      jqXHR => handleAPIError(jqXHR)
    );
  }

  getOptions(selectedPlayers, allPlayers) {
    // Could also add disabled property (which was undocumented)
    // https://github.com/ericgio/react-bootstrap-typeahead/issues/86
    const ids = selectedPlayers.map(player => player.id);
    return allPlayers.filter(player => !ids.includes(player.id));
  }

  // The param for this function is an array
  handleTypeaheadChange(selected) {
    const { handleAddPlayers } = this.props;
    // See https://github.com/ericgio/react-bootstrap-typeahead/blob/master/docs/Methods.md#clear
    if (selected.length) {
      this.typeahead.getInstance().clear();
    }
    handleAddPlayers(selected);
  }

  render() {
    const {
      teamName,
      teamLogo,
      selectedPlayers,
      allPlayers,
      canUpdate,
      teamType,
      handleAddPlayers,
      handleRemovePlayer,
      handleToggleStartingGoalie,
    } = this.props;
    const { seasonRosters } = this.state;
    const sortedPlayers = selectedPlayers ?
      selectedPlayers.sort((a, b) => a.jersey_number - b.jersey_number) : [];

    let element;
    if (selectedPlayers === null) {
      element = (<div className="mt20 text-center"><Loading /></div>);
    } else if (selectedPlayers.length === 0) {
      element = (
        <div className="list-group-item list-group-item-slim text-center">
          There are no players on this roster.
        </div>
      );
    } else if (!canUpdate) {
      element = (
        <div className="list-group-item list-group-item-slim text-center">
          This game roster is currently unavailable.
        </div>
      );
    } else {
      element = (
        <React.Fragment>
          {sortedPlayers.map(player => (
            <PlayerComponent
              key={player.id}
              player={player}
              canUpdate={canUpdate}
              handleRemovePlayer={handleRemovePlayer}
              handleToggleStartingGoalie={handleToggleStartingGoalie}
            />)
          )}
          <div className="text-center mt10">
            {`${selectedPlayers.length} ${pluralize('player', selectedPlayers.length)}`}
          </div>
        </React.Fragment>
      );
    }

    return (
      <div className="col-md-6 game-roster-component">
        <h4 className="text-center">{teamType} Team</h4>
        <div className="text-center mb10">
          {teamLogo && <img className="mr3" src={teamLogo} alt={teamName} />}
          <strong>{teamName}</strong>
        </div>
        {(selectedPlayers !== null && allPlayers !== null) &&
        <React.Fragment>
          <Typeahead
            multiple
            highlightOnlyResult
            selectHintOnEnter
            onChange={this.handleTypeaheadChange}
            options={this.getOptions(selectedPlayers, allPlayers)}
            disabled={!canUpdate}
            emptyLabel="No players found."
            placeholder="Add players via search"
            paginationText="Display more players"
            id={this.typeaheadId}
            ref={(typeahead) => {
              this.typeahead = typeahead;
            }}
          />
          <div className="text-right">
            <SeasonRosterDropdownComponent
              teamType={teamType}
              seasonRosters={seasonRosters}
              handleAddPlayers={handleAddPlayers}
            />
          </div>
        </React.Fragment>
        }
        <div className="list-group">
          {element}
        </div>
      </div>
    );
  }
}

GameRosterComponent.propTypes = {
  teamName: PropTypes.string.isRequired,
  teamId: PropTypes.number.isRequired,
  teamLogo: PropTypes.string.isRequired,
  seasonId: PropTypes.number.isRequired,
  selectedPlayers: PropTypes.arrayOf(playerPropType),
  allPlayers: PropTypes.arrayOf(playerPropType),
  canUpdate: PropTypes.bool.isRequired,
  teamType: PropTypes.oneOf(['Home', 'Away']).isRequired,
  handleAddPlayers: PropTypes.func.isRequired,
  handleRemovePlayer: PropTypes.func.isRequired,
  handleToggleStartingGoalie: PropTypes.func.isRequired,
};

GameRosterComponent.defaultProps = {
  selectedPlayers: null,
  allPlayers: null,
};
