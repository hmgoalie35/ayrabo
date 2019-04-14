import { mount } from 'enzyme/build';
import React from 'react';

import GameRosterComponent from '../GameRosterComponent';
import homePlayers from './homePlayers.json';


const addTypeaheadLabel = players =>
  players.map(p => ({
    ...p,
    label: `#${p.jersey_number} ${p.user.first_name} ${p.user.last_name}`,
  }));

const playersWithLabel = addTypeaheadLabel(homePlayers);

const getComponent = (selectedPlayers, allPlayers, canUpdate = true, handleAddPlayers = jest.fn()) => {
  const props = {
    teamName: 'Green Machine IceCats Midget Minor AA',
    teamId: 3,
    teamLogo: 'logo.png',
    seasonId: 4,
    canUpdate,
    teamType: 'Home',
    selectedPlayers,
    allPlayers,
    handleAddPlayers,
    handleRemovePlayer: jest.fn(),
  };
  return mount(<GameRosterComponent {...props} />);
};

describe('componentDidMount', () => {
  test('fetches season rosters if user can update', () => {
    const spy = jest.spyOn(GameRosterComponent.prototype, 'getSeasonRosters');
    getComponent(playersWithLabel.slice(0, 2), playersWithLabel, true);
    expect(spy).toHaveBeenCalled();
    spy.mockClear();
  });

  test('does not fetch season rosters if user can\'t update', () => {
    const spy = jest.spyOn(GameRosterComponent.prototype, 'getSeasonRosters');
    getComponent(playersWithLabel.slice(0, 2), playersWithLabel, false);
    expect(spy).not.toHaveBeenCalled();
    spy.mockClear();
  });
});

describe('Component functions', () => {
  test('getOptions', () => {
    const allPlayers = playersWithLabel.slice(0, 5);
    const selectedPlayers = playersWithLabel.slice(0, 2);
    const component = getComponent(selectedPlayers, allPlayers);
    const result = component.instance().getOptions(selectedPlayers, allPlayers);
    expect(result).toEqual(allPlayers.slice(2, 5));
  });

  test('handleTypeaheadChange', () => {
    const allPlayers = playersWithLabel.slice(0, 5);
    const selectedPlayers = playersWithLabel.slice(0, 2);
    const player = playersWithLabel.slice(2, 3);
    const handleAddPlayers = jest.fn();
    const component = getComponent(selectedPlayers, allPlayers, true, handleAddPlayers);
    component.instance().handleTypeaheadChange([player]);
    expect(handleAddPlayers).toHaveBeenCalledWith([player]);
    // Could add a test to make sure .clear is called.
  });
});

describe('render', () => {
  test('team type displayed', () => {
    const component = getComponent([], playersWithLabel);
    expect(component.find('h4').text()).toEqual('Home Team');
  });

  test('team name and logo displayed', () => {
    const component = getComponent([], playersWithLabel);
    expect(component.find('strong').text()).toEqual('Green Machine IceCats Midget Minor AA');
    expect(component.find('img').exists()).toBe(true);
  });

  test('selectedPlayers null', () => {
    const component = getComponent(null, playersWithLabel);
    expect(component.find('.list-group').find('i').hasClass('fa-spinner')).toBeTruthy();
  });

  test('selectedPlayers empty', () => {
    const component = getComponent([], playersWithLabel);
    expect(component.find('.list-group').find('.list-group-item').text()).
    toEqual('There are no players on this roster.');
  });

  test('selectedPlayers exist, user can\'t update roster', () => {
    const component = getComponent(playersWithLabel.slice(0, 5), playersWithLabel, false);
    expect(component.find('.list-group-item').text()).
    toEqual('This game roster is currently unavailable.');
  });

  test('selectedPlayers exist, user can update roster', () => {
    const component = getComponent(playersWithLabel.slice(0, 5), playersWithLabel);
    expect(component.find('.list-group-item').length).toEqual(5);
    expect(component.find('.list-group .text-center').text()).toEqual('5 players');
  });
});
