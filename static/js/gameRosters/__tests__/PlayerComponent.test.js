import React from 'react';
import { mount } from 'enzyme';

import PlayerComponent from '../PlayerComponent';
import homePlayers from './homePlayers.json';


const homeTeamPlayer = homePlayers[0];

const getComponent = (canUpdate = true, handleRemovePlayer = jest.fn()) => {
  const props = {
    player: homeTeamPlayer,
    canUpdate,
    handleRemovePlayer,
  };
  return mount(<PlayerComponent {...props} />);
};

describe('render', () => {
  test('player is displayed', () => {
    const component = getComponent();
    expect(component.find('span').first().text()).toEqual('#1 Caleb Gordon C');
  });

  test('can update false', () => {
    const component = getComponent(false);
    expect(component.find('.list-group-item').hasClass('disabled')).toBeTruthy();
    expect(component.find('.fa-trash').exists()).toBeFalsy();
  });

  test('can update true', () => {
    const component = getComponent(true);
    const tooltipComponent = component.find('[data-toggle="tooltip"]');
    expect(tooltipComponent.props().title).toEqual('Remove player');
    expect(tooltipComponent.find('.fa-trash').exists()).toBeTruthy();
  });

  test('Remove player event handler', () => {
    const handleRemovePlayer = jest.fn();
    const component = getComponent(true, handleRemovePlayer);
    component.find('a[role="button"]').simulate('click');
    expect(handleRemovePlayer).toHaveBeenCalledWith(homeTeamPlayer);
  });
});
