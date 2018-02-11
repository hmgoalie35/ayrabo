import React from 'react';
import PropTypes from 'prop-types';

import GameRosterComponent from './GameRosterComponent';
import APIClient from '../common/APIClient';
import { showAPIErrorMessage } from '../common/utils';


export default class GameRostersUpdateComponent extends React.Component {
  constructor(props) {
    super(props);

    this.client = new APIClient();
    this.getPlayers = this.getPlayers.bind(this);
    this.getRosters = this.getRosters.bind(this);
    this.onAPIFailure = this.onAPIFailure.bind(this);

    this.state = {
      // Ids of players already on the rosters
      // homeTeamPlayerIds: null,
      // awayTeamPlayerIds: null,
      // All active players for the teams
      homeTeamPlayers: null,
      awayTeamPlayers: null,
      // Rosters being manipulated by the user
      selectedHomeTeamPlayers: null,
      selectedAwayTeamPlayers: null,
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
      this.setState({
        homeTeamPlayers,
        awayTeamPlayers,
        selectedHomeTeamPlayers: this.cleanPlayers(homeTeamPlayerIds, homeTeamPlayers),
        selectedAwayTeamPlayers: this.cleanPlayers(awayTeamPlayerIds, awayTeamPlayers),
      });
    }, this.onAPIFailure);
  }

  /**
   * Takes a list of player ids and returns an array of the corresponding player objects.
   * @param playerIds Array of player ids
   * @param players Array of player objects
   */
  cleanPlayers(playerIds, players) {
    return playerIds.map(id => players.find(el => id === el.id));
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
    } = this.state;

    console.log(homeTeamPlayers, awayTeamPlayers);

    return (
      <div>

        <form>
          <div className="row">
            <GameRosterComponent
              team={homeTeamName}
              players={selectedHomeTeamPlayers}
              canUpdate={canUpdateHomeTeamRoster}
              teamType="Home"
            />
            <GameRosterComponent
              team={awayTeamName}
              players={selectedAwayTeamPlayers}
              canUpdate={canUpdateAwayTeamRoster}
              teamType="Away"
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
                >Update
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
