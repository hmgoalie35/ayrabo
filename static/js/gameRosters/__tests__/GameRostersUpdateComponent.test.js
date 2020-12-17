import React from 'react';
import { mount } from 'enzyme';

import GameRostersUpdateComponent from '../GameRostersUpdateComponent';
import GameRosterComponent from '../GameRosterComponent';
import homePlayers from './homePlayers.json';
import homeGamePlayers from './homeGamePlayers.json';
import awayPlayers from './awayPlayers.json';
import awayGamePlayers from './awayGamePlayers.json';


const homeTeam = {
  id: 201,
  name: 'Green Machine IceCats Midget Minor AA',
};

const awayTeam = {
  id: 208,
  name: 'Aviator Gulls Midget Minor AA',
};

const homeTeamPlayer = {
  id: 3061,
  user: {
    id: 3062,
    first_name: 'Caleb',
    last_name: 'Gordon',
  },
  sport: 1,
  team: 201,
  jersey_number: 1,
  is_active: true,
  position: 'C',
  handedness: 'Left',
};

const awayTeamPlayer = {
  id: 3215,
  user: {
    id: 3216,
    first_name: 'Robert',
    last_name: 'Carney',
  },
  sport: 1,
  team: 208,
  jersey_number: 1,
  is_active: true,
  position: 'C',
  handedness: 'Left',
};

const sportId = 1;
const gameId = 3;
const seasonId = 5;

beforeEach(() => {
  GameRosterComponent.prototype.getSeasonRosters = jest.fn();
});

const getComponent = (canUpdateHomeTeamRoster = true, canUpdateAwayTeamRoster = false) => {
  const props = {
    sportId,
    gameId,
    seasonId,
    homeTeamId: homeTeam.id,
    homeTeamName: homeTeam.name,
    awayTeamId: awayTeam.id,
    awayTeamName: awayTeam.name,
    canUpdateHomeTeamRoster,
    canUpdateAwayTeamRoster,
  };
  return mount(<GameRostersUpdateComponent {...props} />);
};

const addTypeaheadLabel = players => players.map(p => ({
  ...p,
  label: `#${p.jersey_number} ${p.user.first_name} ${p.user.last_name}`,
}));

const stripId = (gamePlayer) => {
  const temp = Object.assign({}, gamePlayer);
  delete temp['id'];
  return temp;
}

describe('componentDidMount', () => {
  test('fetch players for the home and away teams', () => {
    const mockGetPlayers = jest.fn();
    GameRostersUpdateComponent.prototype.getPlayers = mockGetPlayers;
    getComponent();
    expect(mockGetPlayers).toHaveBeenCalledWith(homeTeam.id);
    expect(mockGetPlayers).toHaveBeenCalledWith(awayTeam.id);
  });

  test('fetch game rosters after the players have been fetched', () => {
    const mockGetPlayers = jest.fn();
    mockGetPlayers.mockReturnValueOnce(homePlayers).mockReturnValueOnce(awayPlayers);
    const mockGetRosters = jest.fn();
    GameRostersUpdateComponent.prototype.getRosters = mockGetRosters;
    GameRostersUpdateComponent.prototype.getPlayers = mockGetPlayers;
    getComponent();
    expect(mockGetRosters).toHaveBeenCalledWith(homePlayers, awayPlayers, sportId, gameId);
  });
});

describe('cleanPlayers', () => {
  test('merges game players and player objects', () => {
    const mergedHomePlayer = {
      "id": 3061,
      "user": {
        "id": 3062,
        "first_name": "Caleb",
        "last_name": "Gordon"
      },
      "sport": 1,
      "team": 201,
      "jersey_number": 1,
      "is_active": true,
      "position": "C",
      "handedness": "Left",
      "game": 3,
      "is_starting": false,
      "player": 3061,
      "team": 201
    };

    const component = getComponent();
    const result = component.instance().cleanPlayers([homeGamePlayers[0]], homePlayers);
    expect(result[0]).toEqual(mergedHomePlayer);
  });
});

describe('addTypeaheadLabel', () => {
  test('adds label key to all players', () => {
    const component = getComponent();
    const result = component.instance().addTypeaheadLabel([homeTeamPlayer]);
    expect(result[0].label).toEqual('#1 Caleb Gordon C');
  });
});

describe('Adding/removing players', () => {
  let homeTeamPlayers;
  let awayTeamPlayers;
  let component;
  let selectedHomeTeamPlayers;
  let selectedAwayTeamPlayers;

  beforeEach(() => {
    homeTeamPlayers = addTypeaheadLabel(homePlayers);
    awayTeamPlayers = addTypeaheadLabel(awayPlayers);
    component = getComponent(true, true);
    // Prevents tooltip() not being defined error
    component.instance().componentDidUpdate = jest.fn();
    selectedHomeTeamPlayers = homeTeamPlayers.slice(1, 6);
    selectedAwayTeamPlayers = awayTeamPlayers.slice(1, 6);

    component.setState({
      homeTeamPlayers,
      awayTeamPlayers,
      selectedHomeTeamPlayers,
      selectedAwayTeamPlayers,
    });
  });

  test('addPlayers uniq', () => {
    const result = component.instance().addPlayers(
      selectedHomeTeamPlayers, selectedHomeTeamPlayers);
    expect(result.length).toEqual(5);
  });

  test('handleAddHomeTeamPlayer', () => {
    expect(selectedHomeTeamPlayers.map(p => p.id)).not.toContain(3061);
    expect(component.state('disableUpdateButton')).toBe(true);

    component.instance().handleAddHomeTeamPlayers([homeTeamPlayer]);
    expect(component.state('selectedHomeTeamPlayers').map(p => p.id)).toContain(3061);
    expect(component.state('disableUpdateButton')).toBe(false);
  });

  test('handleRemoveHomeTeamPlayer', () => {
    expect(selectedHomeTeamPlayers.map(p => p.id)).toContain(3062);
    expect(component.state('disableUpdateButton')).toBe(true);

    component.instance().handleRemoveHomeTeamPlayer(homeTeamPlayers[1]);
    expect(component.state('selectedHomeTeamPlayers').map(p => p.id)).not.toContain(3062);
    expect(component.state('disableUpdateButton')).toBe(false);
  });

  test('handleAddAwayTeamPlayer', () => {
    expect(selectedAwayTeamPlayers.map(p => p.id)).not.toContain(3215);
    expect(component.state('disableUpdateButton')).toBe(true);

    component.instance().handleAddAwayTeamPlayers([awayTeamPlayer]);
    expect(component.state('selectedAwayTeamPlayers').map(p => p.id)).toContain(3215);
    expect(component.state('disableUpdateButton')).toBe(false);
  });

  test('handleRemoveAwayTeamPlayer', () => {
    expect(selectedAwayTeamPlayers.map(p => p.id)).toContain(3216);
    expect(component.state('disableUpdateButton')).toBe(true);

    component.instance().handleRemoveAwayTeamPlayer(awayTeamPlayers[1]);
    expect(component.state('selectedAwayTeamPlayers').map(p => p.id)).not.toContain(3216);
    expect(component.state('disableUpdateButton')).toBe(false);
  });
});

describe('handleSubmit', () => {
  test('Adds players', async () => {
    const component = getComponent(true, true);
    // We have the function resolve some dummy value, we could add the correct api response.
    const mockClientPost = jest.fn();
    mockClientPost.mockReturnValueOnce($.Deferred());
    component.instance().client.post = mockClientPost;

    // Prevents tooltip() not being defined error
    component.instance().componentDidUpdate = jest.fn();
    component.setState({
      selectedHomeTeamPlayers: [],
      selectedAwayTeamPlayers: [],
      savedHomeTeamGamePlayers: [],
      savedAwayTeamGamePlayers: [],
    });
    component.instance().handleAddHomeTeamPlayers([homePlayers[0]]);
    component.instance().handleAddHomeTeamPlayers([homePlayers[1]]);
    component.instance().handleAddAwayTeamPlayers([awayPlayers[0]]);
    component.find('form').simulate('submit');

    await expect(mockClientPost).toHaveBeenCalledWith(
      `sports/${sportId}/games/${gameId}/players/bulk/create`,
      [
        stripId(homeGamePlayers[0]),
        stripId(homeGamePlayers[1]),
        stripId(awayGamePlayers[0])
      ]
    );
  });
  test('Removes players', async () => {
    const component = getComponent(true, true);
    // We have the function resolve some dummy value, we could add the correct api response.
    const mockClientPost = jest.fn();
    mockClientPost.mockReturnValueOnce($.Deferred());
    component.instance().client.post = mockClientPost;

    // Prevents tooltip() not being defined error
    component.instance().componentDidUpdate = jest.fn();
    component.setState({
      selectedHomeTeamPlayers: [],
      selectedAwayTeamPlayers: [],
      savedHomeTeamGamePlayers: [homeGamePlayers[0]],
      savedAwayTeamGamePlayers: [awayGamePlayers[0]],
    });
    component.instance().handleRemoveHomeTeamPlayer(homePlayers[0]);
    component.instance().handleRemoveAwayTeamPlayer(awayPlayers[0]);
    component.find('form').simulate('submit');

    await expect(mockClientPost).toHaveBeenCalledWith(
      `sports/${sportId}/games/${gameId}/players/bulk/delete`,
      [
        {
          id: homeGamePlayers[0].id
        },
        {
          id: awayGamePlayers[0].id
        }
      ],
    );
  });
  test('Updates players', async () => {
    const component = getComponent(true, true);
    // We have the function resolve some dummy value, we could add the correct api response.
    const mockClientPost = jest.fn();
    mockClientPost.mockReturnValueOnce($.Deferred());
    component.instance().client.post = mockClientPost;

    // Prevents tooltip() not being defined error
    component.instance().componentDidUpdate = jest.fn();
    component.setState({
      selectedHomeTeamPlayers: [homePlayers[20]],
      selectedAwayTeamPlayers: [awayPlayers[20]],
      savedHomeTeamGamePlayers: [homeGamePlayers[20]],
      savedAwayTeamGamePlayers: [awayGamePlayers[20]],
    });
    component.instance().handleToggleStartingGoalie(homePlayers[20], true);
    component.instance().handleToggleStartingGoalie(awayPlayers[20], true);
    component.find('form').simulate('submit');

    await expect(mockClientPost).toHaveBeenCalledWith(
      `sports/${sportId}/games/${gameId}/players/bulk/update`,
      [
        {
          id: homeGamePlayers[20].id,
          is_starting: true
        },
        {
          id: awayGamePlayers[20].id,
          is_starting: true
        }
      ],
    );
  });
  test('All actions', async () => {
    const component = getComponent(true, true);
    // We have the function resolve some dummy value, we could add the correct api response.
    const mockClientPost = jest.fn();
    mockClientPost.mockReturnValue($.Deferred());
    component.instance().client.post = mockClientPost;

    // Prevents tooltip() not being defined error
    component.instance().componentDidUpdate = jest.fn();
    component.setState({
      selectedHomeTeamPlayers: [homePlayers[20]],
      selectedAwayTeamPlayers: [awayPlayers[20]],
      savedHomeTeamGamePlayers: [homeGamePlayers[1], homeGamePlayers[20]],
      savedAwayTeamGamePlayers: [awayGamePlayers[1], awayGamePlayers[20]]
    });
    component.instance().handleAddHomeTeamPlayers([homePlayers[0]]);
    component.instance().handleAddHomeTeamPlayers([awayPlayers[0]]);
    component.instance().handleRemoveHomeTeamPlayer(homePlayers[1]);
    component.instance().handleRemoveAwayTeamPlayer(awayPlayers[1]);
    component.instance().handleToggleStartingGoalie(homePlayers[20], true);
    component.instance().handleToggleStartingGoalie(awayPlayers[20], true);

    component.find('form').simulate('submit');

    await expect(mockClientPost).toHaveBeenNthCalledWith(1,
      `sports/${sportId}/games/${gameId}/players/bulk/create`,
      [
        stripId(homeGamePlayers[0]),
        stripId(awayGamePlayers[0]),
      ]
    );
    await expect(mockClientPost).toHaveBeenNthCalledWith(2,
      `sports/${sportId}/games/${gameId}/players/bulk/update`,
      [
        {
          id: homeGamePlayers[20].id,
          is_starting: true
        },
        {
          id: awayGamePlayers[20].id,
          is_starting: true
        }
      ],
    );
    await expect(mockClientPost).toHaveBeenNthCalledWith(3,
      `sports/${sportId}/games/${gameId}/players/bulk/delete`,
      [
        {
          id: homeGamePlayers[1].id
        },
        {
          id: awayGamePlayers[1].id
        }
      ],
    );
  });
});

describe('render', () => {
  test('renders 2 game roster components', () => {
    const component = getComponent();
    expect(component.find('.game-roster-component').length).toEqual(2);
  });

  test('displays update/cancel buttons if can update home team roster', () => {
    const component = getComponent(true, false);
    expect(component.find('#update-game-roster-btn').exists()).toBeTruthy();
    expect(component.find('#cancel-update-game-roster-btn').exists()).toBeTruthy();
  });

  test('displays update/cancel buttons if can update away team roster', () => {
    const component = getComponent(false, true);
    expect(component.find('#update-game-roster-btn').exists()).toBeTruthy();
    expect(component.find('#cancel-update-game-roster-btn').exists()).toBeTruthy();
  });

  test('does not display update button if cant update home or away team rosters', () => {
    const component = getComponent(false, false);
    expect(component.find('#update-game-roster-btn').exists()).toBeFalsy();
    expect(component.find('#cancel-update-game-roster-btn').exists()).toBeFalsy();
  });

  test('Update/cancel buttons disabled when no changes were made', () => {
    const component = getComponent(true, true);
    // Prevents tooltip() not being defined error
    component.instance().componentDidUpdate = jest.fn();
    component.setState({
      homeTeamPlayers: addTypeaheadLabel(homePlayers),
      awayTeamPlayers: addTypeaheadLabel(awayPlayers),
      selectedHomeTeamPlayers: [],
      selectedAwayTeamPlayers: [],
    });
    expect(component.find('#update-game-roster-btn').prop('disabled')).toBe(true);
    expect(component.find('#cancel-update-game-roster-btn').prop('disabled')).toBe(true);
  });

  test('Update/cancel buttons enabled when there are unsaved changes', () => {
    const component = getComponent(true, true);
    // Prevents tooltip() not being defined error
    component.instance().componentDidUpdate = jest.fn();
    component.setState({
      homeTeamPlayers: addTypeaheadLabel(homePlayers),
      awayTeamPlayers: addTypeaheadLabel(awayPlayers),
      selectedHomeTeamPlayers: [],
      selectedAwayTeamPlayers: [],
    });
    component.instance().handleAddHomeTeamPlayers([homeTeamPlayer]);
    component.update();
    expect(component.find('#update-game-roster-btn').prop('disabled')).toBe(false);
    expect(component.find('#cancel-update-game-roster-btn').prop('disabled')).toBe(false);
  });
});
