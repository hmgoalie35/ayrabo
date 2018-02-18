import React from 'react';
import { mount } from 'enzyme';

import SeasonRosterModalComponent from '../SeasonRosterModalComponent';
import seasonRosters from './seasonRosters.json';

const { $ } = global;
const roster = seasonRosters[0];
const getComponent = (handleAddPlayers = jest.fn()) => {
  const props = {
    roster,
    handleAddPlayers,
  };
  return mount(<SeasonRosterModalComponent {...props} />);
};


describe('render', () => {
  afterEach(() => {
    global.$ = $;
  });

  test('Modal header', () => {
    const component = getComponent();
    expect(component.find('.modal-title').text()).toEqual('Add players from "Main Squad"');
  });

  test('Modal body', () => {
    const component = getComponent();
    const listItems = component.find('.modal-body ul li');
    expect(listItems.length).toEqual(6);
    expect(listItems.first().text()).toEqual('#2 Nicholas Davis C');
  });

  test('Modal footer', () => {
    global.$ = jest.fn(() => ({ modal: () => null }));
    const handleAddPlayers = jest.fn();
    const component = getComponent(handleAddPlayers);
    expect(component.find('.modal-footer button').length).toEqual(2);
    component.find('.btn.btn-success').simulate('click');
    expect(handleAddPlayers).toHaveBeenCalledWith(roster.players);
  });
});
