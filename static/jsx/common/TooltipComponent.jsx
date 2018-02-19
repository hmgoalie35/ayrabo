import React from 'react';
import PropTypes from 'prop-types';


const TooltipComponent = ({ title, placement, children }) => (
  <div data-toggle="tooltip" data-placement={placement} title={title}>
    {children}
  </div>
);

TooltipComponent.propTypes = {
  placement: PropTypes.oneOf(['top', 'left', 'bottom', 'right']).isRequired,
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
};

export default TooltipComponent;
