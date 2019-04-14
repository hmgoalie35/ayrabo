import React from 'react';
import { mount } from 'enzyme/build';

import SeasonRosterDropdownComponent from '../SeasonRosterDropdownComponent';
import seasonRostersData from './seasonRosters.json';


const getComponent = (seasonRosters) => {
  const props = {
    teamType: 'Home',
    seasonRosters,
    handleAddPlayers: jest.fn(),
  };
  return mount(<SeasonRosterDropdownComponent {...props} />);
};

describe('render', () => {
  test('season rosters null', () => {
    const component = getComponent(null);
    const anchorTag = component.find('a');
    expect(component.find('ul').length).toEqual(0);
    expect(anchorTag.prop('disabled')).toBe(true);
    expect(anchorTag.text()).toEqual('Add players via season roster');
  });

  test('season rosters empty', () => {
    const component = getComponent([]);
    expect(component.find('#season-roster-Home').prop('disabled')).toBe(false);
    expect(component.find('ul a').text()).toEqual('There are no season rosters.');
  });

  test('season rosters exist', () => {
    const component = getComponent(seasonRostersData.slice(0, 2));
    const listItems = component.find('ul.dropdown-menu > li');
    expect(listItems.length).toEqual(2);
    expect(listItems.first('a').text()).toEqual('Main Squad');
    const modals = component.find('.modal');
    expect(modals.length).toEqual(2);
  });
});
