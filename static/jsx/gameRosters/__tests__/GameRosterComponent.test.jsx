import React from 'react';
import { mount } from 'enzyme';

import GameRosterComponent from '../GameRosterComponent';
import homePlayers from './homePlayers.json';


const getComponent = (players = null) => {
  const props = {
    team: 'Green Machine IceCats Midget Minor AA',
    canUpdate: true,
    teamType: 'Home',
    players,
  };
  return mount(<GameRosterComponent {...props} />);
};

describe('render', () => {
  test('team type displayed', () => {
    const component = getComponent();
    expect(component.find('h4').text()).toEqual('Home Team');
  });

  test('team name displayed', () => {
    const component = getComponent();
    expect(component.find('strong').text()).toEqual('Green Machine IceCats Midget Minor AA');
  });

  test('players null', () => {
    const component = getComponent(null);
    expect(component.find('.list-group').find('i').hasClass('fa-spinner')).toBeTruthy();
  });

  test('players empty', () => {
    const component = getComponent([]);
    expect(component.find('.list-group').find('.list-group-item').text()).toEqual('There are no players on this roster.');
  });

  test('players exist', () => {
    const component = getComponent(homePlayers.slice(0, 5));
    expect(component.find('.list-group-item').length).toEqual(5);
  });
});
