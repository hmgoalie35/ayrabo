import React from 'react';
import PropTypes from 'prop-types';
import { uniqBy } from 'lodash/array';

import APIClient from '../common/APIClient';
import {
  createNotification,
  handleAPIError,
  pluralize,
  toggleAPIErrorMessage,
} from '../common/utils';
import GameRosterComponent from './GameRosterComponent';


export default class GameRostersUpdateComponent extends React.Component {
  constructor(props) {
    super(props);

    this.client = new APIClient();

    this.getPlayers = this.getPlayers.bind(this);
    this.getRosters = this.getRosters.bind(this);
    this.handleAddHomeTeamPlayers = this.handleAddHomeTeamPlayers.bind(this);
    this.handleAddAwayTeamPlayers = this.handleAddAwayTeamPlayers.bind(this);
    this.handleRemoveHomeTeamPlayer = this.handleRemoveHomeTeamPlayer.bind(this);
    this.handleRemoveAwayTeamPlayer = this.handleRemoveAwayTeamPlayer.bind(this);
    this.handleToggleStartingGoalie = this.handleToggleStartingGoalie.bind(this);
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
      // Current roster state in backend
      savedHomeTeamGamePlayers: null,
      savedAwayTeamGamePlayers: null,
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
        gameId
      );
    });
  }

  componentDidUpdate() {
    $('[data-toggle="tooltip"]').tooltip();
  }

  getPlayers(teamId) {
    return this.client.get(
      `teams/${teamId}/players`,
      { is_active: true }
    ).then(data => data, jqXHR => handleAPIError(jqXHR));
  }

  getRosters(homeTeamPlayers, awayTeamPlayers, sportId, gameId) {
    const { homeTeamId, awayTeamId } = this.props;

    return this.client.get(
      `sports/${sportId}/games/${gameId}/players`
    ).then((data) => {
      const playersByTeam = {};
      playersByTeam[homeTeamId] = [];
      playersByTeam[awayTeamId] = [];
      data.forEach((gamePlayer) => {
        playersByTeam[gamePlayer.team].push(gamePlayer);
      });

      const homeTeamPlayersSynced =
        this.syncPlayersToGamePlayers(homeTeamPlayers, playersByTeam[homeTeamId]);
      const awayTeamPlayersSynced =
        this.syncPlayersToGamePlayers(awayTeamPlayers, playersByTeam[awayTeamId]);

      const homePlayers = this.addTypeaheadLabel(homeTeamPlayersSynced);
      const awayPlayers = this.addTypeaheadLabel(awayTeamPlayersSynced);

      this.setState({
        homeTeamPlayers: homePlayers,
        awayTeamPlayers: awayPlayers,
        selectedHomeTeamPlayers:
          this.filterAndSyncPlayers(homeTeamPlayers, playersByTeam[homeTeamId]),
        selectedAwayTeamPlayers:
          this.filterAndSyncPlayers(awayTeamPlayers, playersByTeam[awayTeamId]),
        savedHomeTeamGamePlayers: playersByTeam[homeTeamId],
        savedAwayTeamGamePlayers: playersByTeam[awayTeamId],
      });
    }, jqXHR => handleAPIError(jqXHR));
  }

  syncPlayersToGamePlayers(players, gamePlayers) {
    return players.map((player) => {
      const gamePlayer = gamePlayers.find(gp => gp.player === player.id);

      return {
        ...gamePlayer,
        ...player,

        // Override is_starting with game player value
        is_starting: gamePlayer ? gamePlayer.is_starting : false,
      };
    });
  }

  addPlayers(currentPlayers, newPlayers) {
    return uniqBy(currentPlayers.concat(newPlayers), 'id');
  }

  removePlayer(currentPlayers, removedPlayer) {
    return currentPlayers.filter(player => player.id !== removedPlayer.id);
  }

  handleToggleStartingGoalie(player, isStarting) {
    const {
      selectedHomeTeamPlayers,
      selectedAwayTeamPlayers,
      homeTeamPlayers,
      awayTeamPlayers,
    } = this.state;
    const { homeTeamId } = this.props;
    const isHomePlayer = player.team === homeTeamId;
    const selectedPlayers = isHomePlayer ? selectedHomeTeamPlayers : selectedAwayTeamPlayers;
    const players = isHomePlayer ? homeTeamPlayers : awayTeamPlayers;

    const setStarter = (selectedPlayer) => {
      const sPlayer = selectedPlayer;
      if (sPlayer.position === 'G') {
        if (sPlayer.id === player.id) {
          sPlayer.is_starting = isStarting;
        } else {
          sPlayer.is_starting = false;
        }
      }
    };

    selectedPlayers.forEach(setStarter);
    players.forEach(setStarter);

    const state = {
      disableUpdateButton: false,
    };

    if (isHomePlayer) {
      state.selectedHomeTeamPlayers = selectedPlayers;
      state.homeTeamPlayers = players;
    } else {
      state.selectedAwayTeamPlayers = selectedPlayers;
      state.awayTeamPlayers = players;
    }

    this.setState(state);
  }

  handleAddHomeTeamPlayers(selected) {
    const { selectedHomeTeamPlayers } = this.state;
    const addedPlayers = this.addPlayers(selectedHomeTeamPlayers, selected);
    this.setState({
      selectedHomeTeamPlayers: addedPlayers,
      disableUpdateButton: false,
    });
  }

  handleRemoveHomeTeamPlayer(removedPlayer) {
    const { selectedHomeTeamPlayers } = this.state;
    const removedPlayers = this.removePlayer(selectedHomeTeamPlayers, removedPlayer);
    this.setState({
      selectedHomeTeamPlayers: removedPlayers,
      disableUpdateButton: false,
    });
  }

  handleAddAwayTeamPlayers(selected) {
    const { selectedAwayTeamPlayers } = this.state;
    const addedPlayers = this.addPlayers(selectedAwayTeamPlayers, selected);
    this.setState({
      selectedAwayTeamPlayers: addedPlayers,
      disableUpdateButton: false,
    });
  }

  handleRemoveAwayTeamPlayer(removedPlayer) {
    const { selectedAwayTeamPlayers } = this.state;
    const removedPlayers = this.removePlayer(selectedAwayTeamPlayers, removedPlayer);
    this.setState({
      selectedAwayTeamPlayers: removedPlayers,
      disableUpdateButton: false,
    });
  }

  buildCreates() {
    const {
      selectedHomeTeamPlayers,
      selectedAwayTeamPlayers,
      savedHomeTeamGamePlayers,
      savedAwayTeamGamePlayers,
    } = this.state;
    const { gameId } = this.props;

    const filterCreates = (selectedData, savedData) => selectedData.filter((player) => {
      const savedPlayer = savedData.find(gp => player.id === gp.player);
      return savedPlayer === undefined;
    }).map(player => ({
      team: player.team,
      player: player.id,
      is_starting: player.is_starting || false,
      game: gameId,
    }));

    let data = [];
    data = data.concat(filterCreates(selectedHomeTeamPlayers, savedHomeTeamGamePlayers));
    data = data.concat(filterCreates(selectedAwayTeamPlayers, savedAwayTeamGamePlayers));

    return data;
  }

  buildUpdates() {
    const {
      selectedHomeTeamPlayers,
      selectedAwayTeamPlayers,
      savedHomeTeamGamePlayers,
      savedAwayTeamGamePlayers,
    } = this.state;

    const filterUpdates = (selectedData, savedData) => selectedData.filter((player) => {
      const savedPlayer = savedData.find(gp => player.id === gp.player);
      return savedPlayer !== undefined && savedPlayer.is_starting !== player.is_starting;
    }).map((player) => {
      const gamePlayer = savedData.find(gp => player.id === gp.player);
      return {
        id: gamePlayer.id,
        is_starting: player.is_starting,
      };
    });

    let data = [];
    data = data.concat(filterUpdates(selectedHomeTeamPlayers, savedHomeTeamGamePlayers));
    data = data.concat(filterUpdates(selectedAwayTeamPlayers, savedAwayTeamGamePlayers));

    return data;
  }

  buildDeletes() {
    const {
      selectedHomeTeamPlayers,
      selectedAwayTeamPlayers,
      savedHomeTeamGamePlayers,
      savedAwayTeamGamePlayers,
    } = this.state;

    const filterDeletes = (selectedData, savedData) => savedData.filter((gp) => {
      const selectedPlayer = selectedData.find(player => player.id === gp.player);
      return selectedPlayer === undefined;
    }).map(player => ({
      id: player.id,
    }));

    let data = [];
    data = data.concat(filterDeletes(selectedHomeTeamPlayers, savedHomeTeamGamePlayers));
    data = data.concat(filterDeletes(selectedAwayTeamPlayers, savedAwayTeamGamePlayers));

    return data;
  }

  handleSubmit(e) {
    e.preventDefault();
    e.stopPropagation();

    const {
      homeTeamPlayers,
      awayTeamPlayers,
    } = this.state;

    const {
      gameId,
      sportId,
    } = this.props;

    let totalActions = 0;

    const creates = this.buildCreates();
    const updates = this.buildUpdates();
    const deletes = this.buildDeletes();

    if (creates.length) totalActions += 1;
    if (updates.length) totalActions += 1;
    if (deletes.length) totalActions += 1;

    let successes = 0;
    const errors = [];

    const handleAlways = () => {
      const allActionsComplete = successes + errors.length === totalActions;
      if (allActionsComplete) {
        if (successes > 0) {
          this.getRosters(homeTeamPlayers, awayTeamPlayers, sportId, gameId);
          this.setState({ disableUpdateButton: true });

          if (successes === totalActions) {
            createNotification('Your updates have been saved.', 'success').show();
          } else {
            createNotification('Some of your updates were not saved. Please refresh and try again.', 'warning').show();
          }
        } else {
          let message = `We experienced ${errors.length} ${pluralize('issue', errors.length)} with your request`;
          message += `<ul>
            ${errors.filter(error => error.non_field_errors != null).map(error => `<li>${error.non_field_errors}</li>`)}
          </ul>`;
          toggleAPIErrorMessage('show', message);
        }
      }
    };

    const handleSuccess = () => {
      successes += 1;
    };

    const handleError = (jqXHR) => {
      errors.push(jqXHR.responseJSON);
      handleAPIError(jqXHR);
    };

    if (creates.length) {
      this.client.post(
        `sports/${sportId}/games/${gameId}/players/bulk/create`,
        creates
      ).then(handleSuccess, handleError).always(handleAlways);
    }

    if (updates.length) {
      this.client.post(
        `sports/${sportId}/games/${gameId}/players/bulk/update`,
        updates
      ).then(handleSuccess, handleError).always(handleAlways);
    }

    if (deletes.length) {
      this.client.post(
        `sports/${sportId}/games/${gameId}/players/bulk/delete`,
        deletes
      ).then(handleSuccess, handleError).always(handleAlways);
    }

    if (totalActions === 0) {
      createNotification('No updates were made to rosters, double check your changes and try again', 'warning').show();
      this.getRosters(homeTeamPlayers, awayTeamPlayers, sportId, gameId);
      this.setState({ disableUpdateButton: true });
    }
  }

  /**
   * Takes a list of game player data and returns an array of merged player objects
   * @param players Array of player objects
   * @param gamePlayers Array of game player objects
   */
  filterAndSyncPlayers(players, gamePlayers) {
    const filteredPlayers = players.filter((p) => {
      const gamePlayer = gamePlayers.find(gp => p.id === gp.player);
      return gamePlayer !== undefined;
    });

    return this.syncPlayersToGamePlayers(filteredPlayers, gamePlayers);
  }

  addTypeaheadLabel(players) {
    return players.map(player => ({
      ...player,
      label: `#${player.jersey_number} ${player.user.first_name} ${player.user.last_name} ${player.position}`,
    }));
  }

  render() {
    const {
      homeTeamName,
      homeTeamId,
      homeTeamLogo,
      awayTeamName,
      awayTeamId,
      awayTeamLogo,
      canUpdateHomeTeamRoster,
      canUpdateAwayTeamRoster,
      seasonId,
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
              teamName={homeTeamName}
              teamId={homeTeamId}
              teamLogo={homeTeamLogo}
              seasonId={seasonId}
              selectedPlayers={selectedHomeTeamPlayers}
              allPlayers={homeTeamPlayers}
              canUpdate={canUpdateHomeTeamRoster}
              teamType="Home"
              handleAddPlayers={this.handleAddHomeTeamPlayers}
              handleRemovePlayer={this.handleRemoveHomeTeamPlayer}
              handleToggleStartingGoalie={this.handleToggleStartingGoalie}
            />
            <GameRosterComponent
              teamName={awayTeamName}
              teamId={awayTeamId}
              teamLogo={awayTeamLogo}
              seasonId={seasonId}
              selectedPlayers={selectedAwayTeamPlayers}
              allPlayers={awayTeamPlayers}
              canUpdate={canUpdateAwayTeamRoster}
              teamType="Away"
              handleAddPlayers={this.handleAddAwayTeamPlayers}
              handleRemovePlayer={this.handleRemoveAwayTeamPlayer}
              handleToggleStartingGoalie={this.handleToggleStartingGoalie}
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
  seasonId: PropTypes.number.isRequired,
  homeTeamId: PropTypes.number.isRequired,
  homeTeamName: PropTypes.string.isRequired,
  homeTeamLogo: PropTypes.string,
  awayTeamId: PropTypes.number.isRequired,
  awayTeamName: PropTypes.string.isRequired,
  awayTeamLogo: PropTypes.string,
  canUpdateHomeTeamRoster: PropTypes.bool.isRequired,
  canUpdateAwayTeamRoster: PropTypes.bool.isRequired,
};

GameRostersUpdateComponent.defaultProps = {
  homeTeamLogo: '',
  awayTeamLogo: '',
};
