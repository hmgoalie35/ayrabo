import React from 'react';
import { mount } from 'enzyme';

import GameRostersUpdateComponent from '../GameRostersUpdateComponent';
import homePlayers from './homePlayers.json';
import awayPlayers from './awayPlayers.json';


const homeTeam = {
  id: 1,
  name: 'Green Machine IceCats Midget Minor AA',
};

const awayTeam = {
  id: 2,
  name: 'Aviator Gulls Midget Minor AA',
};

const sportId = 1;
const gameId = 100;

const getComponent = (canUpdateHomeTeamRoster = true, canUpdateAwayTeamRoster = false) => {
  const props = {
    sportId,
    gameId,
    homeTeamId: homeTeam.id,
    homeTeamName: homeTeam.name,
    awayTeamId: awayTeam.id,
    awayTeamName: awayTeam.name,
    canUpdateHomeTeamRoster,
    canUpdateAwayTeamRoster,
  };
  return mount(<GameRostersUpdateComponent{...props} />);
};

describe('componentDidMount', () => {
  test('fetch players for the home and away teams', () => {
    const spy = jest.spyOn(GameRostersUpdateComponent.prototype, 'getPlayers');
    getComponent();
    expect(spy).toHaveBeenCalledWith(homeTeam.id);
    expect(spy).toHaveBeenCalledWith(awayTeam.id);
    spy.mockClear();
  });

  test('fetch game rosters after the players have been fetched', () => {
    const spy = jest.spyOn(GameRostersUpdateComponent.prototype, 'getRosters');
    GameRostersUpdateComponent.prototype.getPlayers = jest.fn()
      .mockReturnValueOnce(homePlayers).mockReturnValueOnce(awayPlayers);
    getComponent();
    expect(spy).toHaveBeenCalledWith(homePlayers, awayPlayers, sportId, gameId);
    spy.mockClear();
  });
});

describe('cleanPlayers', () => {
  test('converts ids into player objects', () => {
    const component = getComponent();
    const result = component.instance().cleanPlayers([3061, 3062], homePlayers);
    expect(result[0]).toEqual(homePlayers[0]);
    expect(result[1]).toEqual(homePlayers[1]);
  });
});

describe('render', () => {
  test('renders 2 game roster components', () => {
    const component = getComponent();
    expect(component.find('.game-roster-component').length).toEqual(2);
  });

  test('displays update button if can update home team roster', () => {
    const component = getComponent(true, false);
    expect(component.find('#update-game-roster-btn').exists()).toBeTruthy();
  });

  test('displays update button if can update away team roster', () => {
    const component = getComponent(false, true);
    expect(component.find('#update-game-roster-btn').exists()).toBeTruthy();
  });

  test('does not display update button if cant update home or away team rosters', () => {
    const component = getComponent(false, false);
    expect(component.find('#update-game-roster-btn').exists()).toBeFalsy();
  });
});
