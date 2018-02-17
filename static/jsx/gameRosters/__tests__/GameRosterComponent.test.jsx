import React from 'react';
import { mount } from 'enzyme';

import GameRosterComponent from '../GameRosterComponent';
import homePlayers from './homePlayers.json';


const addTypeaheadLabel = players =>
  players.map(p => ({
    ...p,
    label: `#${p.jersey_number} ${p.user.first_name} ${p.user.last_name}`,
  }));

const playersWithLabel = addTypeaheadLabel(homePlayers);

const getComponent = (selectedPlayers, allPlayers, canUpdate = true, handleAddPlayer = jest.fn()) => {
  const props = {
    team: 'Green Machine IceCats Midget Minor AA',
    canUpdate,
    teamType: 'Home',
    selectedPlayers,
    allPlayers,
    handleAddPlayer,
    handleRemovePlayer: jest.fn(),
  };
  return mount(<GameRosterComponent {...props} />);
};

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
    const handleAddPlayer = jest.fn();
    const component = getComponent(selectedPlayers, allPlayers, true, handleAddPlayer);
    component.instance().handleTypeaheadChange([player]);
    expect(handleAddPlayer).toHaveBeenCalledWith([player]);
    // Could add a test to make sure .clear is called.
  });
});

describe('render', () => {
  test('team type displayed', () => {
    const component = getComponent([], playersWithLabel);
    expect(component.find('h4').text()).toEqual('Home Team');
  });

  test('team name displayed', () => {
    const component = getComponent([], playersWithLabel);
    expect(component.find('strong').text()).toEqual('Green Machine IceCats Midget Minor AA');
  });

  test('selectedPlayers null', () => {
    const component = getComponent(null, playersWithLabel);
    expect(component.find('.list-group').find('i').hasClass('fa-spinner')).toBeTruthy();
  });

  test('selectedPlayers empty', () => {
    const component = getComponent([], playersWithLabel);
    expect(component.find('.list-group').find('.list-group-item').text()).toEqual('There are no players on this roster.');
  });

  test('selectedPlayers exist, user can\'t update roster', () => {
    const component = getComponent(playersWithLabel.slice(0, 5), playersWithLabel, false);
    expect(component.find('.list-group-item').text()).toEqual('This game roster is currently unavailable.');
  });

  test('selectedPlayers exist, user can update roster', () => {
    const component = getComponent(playersWithLabel.slice(0, 5), playersWithLabel);
    expect(component.find('.list-group-item').length).toEqual(5);
    expect(component.find('.list-group .text-center').text()).toEqual('5 players');
  });
});
