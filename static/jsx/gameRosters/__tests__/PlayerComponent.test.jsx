import React from 'react';
import { mount } from 'enzyme';

import PlayerComponent from '../PlayerComponent';
import homePlayers from './homePlayers.json';


const getComponent = (canUpdate = true) => {
  const props = {
    player: homePlayers[0],
    canUpdate,
  };
  return mount(<PlayerComponent {...props} />);
};

describe('render', () => {
  test('user \'s name is displayed', () => {
    const component = getComponent();
    expect(component.find('span').first().text()).toEqual('Caleb Gordon');
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
});
