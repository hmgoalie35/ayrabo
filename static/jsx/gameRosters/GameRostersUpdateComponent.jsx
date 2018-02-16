import React from 'react';
import PropTypes from 'prop-types';

import GameRosterComponent from './GameRosterComponent';
import APIClient from '../common/APIClient';
import { createNotification, showAPIErrorMessage } from '../common/utils';


export default class GameRostersUpdateComponent extends React.Component {
  constructor(props) {
    super(props);

    this.client = new APIClient();

    this.getPlayers = this.getPlayers.bind(this);
    this.getRosters = this.getRosters.bind(this);
    this.onAPIFailure = this.onAPIFailure.bind(this);
    this.handleAddHomeTeamPlayer = this.handleAddHomeTeamPlayer.bind(this);
    this.handleAddAwayTeamPlayer = this.handleAddAwayTeamPlayer.bind(this);
    this.handleRemoveHomeTeamPlayer = this.handleRemoveHomeTeamPlayer.bind(this);
    this.handleRemoveAwayTeamPlayer = this.handleRemoveAwayTeamPlayer.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.addPlayers = this.addPlayers.bind(this);
    this.removePlayer = this.removePlayer.bind(this);

    this.state = {
      // All active players for the teams
      homeTeamPlayers: null,
      awayTeamPlayers: null,
      // Rosters being manipulated by the user
      selectedHomeTeamPlayers: null,
      selectedAwayTeamPlayers: null,
      disableUpdateButton: true,
    };
  }

  componentDidMount() {
    const {
      sportId,
      gameId,
      homeTeamId,
      awayTeamId,
    } = this.props;

    // Waits for the 2 ajax requests to finish, then calls getRosters.
    $.when(
      this.getPlayers(homeTeamId),
      this.getPlayers(awayTeamId),
    ).then((homeTeamPlayersResult, awayTeamPlayersResult) => {
      this.getRosters(
        homeTeamPlayersResult,
        awayTeamPlayersResult,
        sportId,
        gameId,
      );
    });
  }

  componentDidUpdate() {
    $('[data-toggle="tooltip"]').tooltip();
  }

  onAPIFailure(jqXHR) {
    if (jqXHR.status === 400) {
      console.info(jqXHR.responseJSON);
    } else {
      showAPIErrorMessage();
    }
  }

  getPlayers(teamId) {
    return this.client.get(`teams/${teamId}/players`, { is_active: true }).then(data => data, this.onAPIFailure);
  }

  getRosters(homeTeamPlayers, awayTeamPlayers, sportId, gameId) {
    return this.client.get(`sports/${sportId}/games/${gameId}/rosters`).then((data) => {
      const { home_players: homeTeamPlayerIds, away_players: awayTeamPlayerIds } = data;
      const homePlayers = this.addTypeaheadLabel(homeTeamPlayers);
      const awayPlayers = this.addTypeaheadLabel(awayTeamPlayers);
      this.setState({
        homeTeamPlayers: homePlayers,
        awayTeamPlayers: awayPlayers,
        selectedHomeTeamPlayers: this.cleanPlayers(homeTeamPlayerIds, homePlayers),
        selectedAwayTeamPlayers: this.cleanPlayers(awayTeamPlayerIds, awayPlayers),
      });
    }, this.onAPIFailure);
  }

  addPlayers(currentPlayers, newPlayers) {
    return currentPlayers.concat(newPlayers);
  }

  removePlayer(currentPlayers, removedPlayer) {
    return currentPlayers.filter(player => player.id !== removedPlayer.id);
  }

  handleAddHomeTeamPlayer(selected) {
    const { selectedHomeTeamPlayers } = this.state;
    this.setState({
      selectedHomeTeamPlayers: this.addPlayers(selectedHomeTeamPlayers, selected),
      disableUpdateButton: false,
    });
  }

  handleRemoveHomeTeamPlayer(removedPlayer) {
    const { selectedHomeTeamPlayers } = this.state;
    this.setState({
      selectedHomeTeamPlayers: this.removePlayer(selectedHomeTeamPlayers, removedPlayer),
      disableUpdateButton: false,
    });
  }

  handleAddAwayTeamPlayer(selected) {
    const { selectedAwayTeamPlayers } = this.state;
    this.setState({
      selectedAwayTeamPlayers: this.addPlayers(selectedAwayTeamPlayers, selected),
      disableUpdateButton: false,
    });
  }

  handleRemoveAwayTeamPlayer(removedPlayer) {
    const { selectedAwayTeamPlayers } = this.state;
    this.setState({
      selectedAwayTeamPlayers: this.removePlayer(selectedAwayTeamPlayers, removedPlayer),
      disableUpdateButton: false,
    });
  }

  handleSubmit(e) {
    e.preventDefault();
    e.stopPropagation();

    const { gameId, sportId } = this.props;
    const { selectedHomeTeamPlayers, selectedAwayTeamPlayers } = this.state;
    const homePlayerIds = selectedHomeTeamPlayers.map(player => player.id);
    const awayPlayerIds = selectedAwayTeamPlayers.map(player => player.id);
    const onSuccess = () => {
      this.setState({ disableUpdateButton: true });
      createNotification('Your updates have been saved.', 'success').show();
    };

    this.client.put(`sports/${sportId}/games/${gameId}/rosters`, {
      home_players: homePlayerIds,
      away_players: awayPlayerIds,
    }).then(onSuccess, this.onAPIFailure);
  }

  /**
   * Takes a list of player ids and returns an array of the corresponding player objects.
   * @param playerIds Array of player ids
   * @param players Array of player objects
   */
  cleanPlayers(playerIds, players) {
    return playerIds.map(id => players.find(el => id === el.id));
  }

  addTypeaheadLabel(players) {
    return players.map(player => ({
      ...player,
      label: `#${player.jersey_number} ${player.user.first_name} ${player.user.last_name}`,
    }));
  }

  render() {
    const {
      homeTeamName,
      awayTeamName,
      canUpdateHomeTeamRoster,
      canUpdateAwayTeamRoster,
    } = this.props;

    const {
      selectedHomeTeamPlayers,
      selectedAwayTeamPlayers,
      homeTeamPlayers,
      awayTeamPlayers,
      disableUpdateButton,
    } = this.state;

    return (
      <div className="game-rosters-update-component">

        <form onSubmit={this.handleSubmit}>
          <div className="row">
            <GameRosterComponent
              team={homeTeamName}
              selectedPlayers={selectedHomeTeamPlayers}
              allPlayers={homeTeamPlayers}
              canUpdate={canUpdateHomeTeamRoster}
              teamType="Home"
              handleAddPlayer={this.handleAddHomeTeamPlayer}
              handleRemovePlayer={this.handleRemoveHomeTeamPlayer}
            />
            <GameRosterComponent
              team={awayTeamName}
              selectedPlayers={selectedAwayTeamPlayers}
              allPlayers={awayTeamPlayers}
              canUpdate={canUpdateAwayTeamRoster}
              teamType="Away"
              handleAddPlayer={this.handleAddAwayTeamPlayer}
              handleRemovePlayer={this.handleRemoveAwayTeamPlayer}
            />
          </div>

          {(canUpdateHomeTeamRoster || canUpdateAwayTeamRoster) &&
          <div className="row">
            <div className="col-md-12">
              <div className="text-center">
                <button
                  className="btn btn-success"
                  type="submit"
                  id="update-game-roster-btn"
                  disabled={disableUpdateButton}
                >
                  Update
                </button>
                <button
                  className="btn btn-link"
                  type="button"
                  id="cancel-update-game-roster-btn"
                  /* onClick handler doesn't get called when the button is disabled */
                  onClick={() => window.location.reload()}
                  disabled={disableUpdateButton}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
          }
        </form>

      </div>
    );
  }
}

GameRostersUpdateComponent.propTypes = {
  gameId: PropTypes.number.isRequired,
  sportId: PropTypes.number.isRequired,
  homeTeamId: PropTypes.number.isRequired,
  homeTeamName: PropTypes.string.isRequired,
  awayTeamId: PropTypes.number.isRequired,
  awayTeamName: PropTypes.string.isRequired,
  canUpdateHomeTeamRoster: PropTypes.bool.isRequired,
  canUpdateAwayTeamRoster: PropTypes.bool.isRequired,
};
