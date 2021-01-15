import React from 'react';
import { mount } from 'enzyme';

import PlayerComponent from '../PlayerComponent';
import homePlayers from './homePlayers.json';


const setAsStarter = (player) => {
  player.is_starting = true;
  return player;
};

const homeTeamPlayer = homePlayers[0];
const startingGoalie = setAsStarter(homePlayers[20]);
const goalie = homePlayers[21];

const getComponent = (player, canUpdate = true, handleRemovePlayer = jest.fn(), handleToggleStartingGoalie = jest.fn()) => {
  const props = {
    player,
    canUpdate,
    handleRemovePlayer,
    handleToggleStartingGoalie
  };
  return mount(<PlayerComponent {...props} />);
};

describe('render', () => {
  test('player is displayed', () => {
    const component = getComponent(homeTeamPlayer);
    expect(component.find('span').first().text()).toEqual('#1 Caleb Gordon C');
  });

  test('can update false', () => {
    const component = getComponent(homeTeamPlayer, false);
    expect(component.find('.list-group-item').hasClass('disabled')).toBeTruthy();
    expect(component.find('.fa-trash').exists()).toBeFalsy();
  });

  test('can update true', () => {
    const component = getComponent(homeTeamPlayer, true);
    const tooltipComponent = component.find('[data-toggle="tooltip"]');
    expect(tooltipComponent.props().title).toEqual('Remove player');
    expect(tooltipComponent.find('.fa-trash').exists()).toBeTruthy();
  });

  test('Remove player event handler', () => {
    const handleRemovePlayer = jest.fn();
    const component = getComponent(homeTeamPlayer, true, handleRemovePlayer);
    component.find('a[role="button"]').simulate('click');
    expect(handleRemovePlayer).toHaveBeenCalledWith(homeTeamPlayer);
  });

  test('starting goalie toggle', () => {
    const component = getComponent(startingGoalie);
    const button = component.find('a[role="button"]').first();
    expect(button.text()).toEqual('Starter');
    expect(button.simulate('mouseEnter').text()).toEqual('Remove Starter');
    expect(button.simulate('mouseLeave').text()).toEqual('Starter');
  });

  test('not starting goalie toggle', () => {
    const component = getComponent(goalie);
    const button = component.find('a[role="button"]').first();
    expect(button.text()).toEqual('Set as Starter');
  });
});
