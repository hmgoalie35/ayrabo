import PropTypes from 'prop-types';


export const userPropType = PropTypes.shape({
  id: PropTypes.number.isRequired,
  first_name: PropTypes.string.isRequired,
  last_name: PropTypes.string.isRequired,
});

export const playerPropType = PropTypes.shape({
  id: PropTypes.number.isRequired,
  user: userPropType.isRequired,
});
