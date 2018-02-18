/* eslint-disable jsx-a11y/anchor-is-valid,jsx-a11y/click-events-have-key-events */
import React from 'react';
import PropTypes from 'prop-types';
import { noop } from 'lodash/util';

import { seasonRosterPropType } from '../common/proptypes';


const SeasonRosterDropdownComponent = (props) => {
  const { teamType, seasonRosters } = props;
  const id = `season-roster-${teamType}`;

  let listItems;
  if (seasonRosters === null) {
    listItems = null;
  } else if (seasonRosters.length === 0) {
    listItems = (
      <li><a tabIndex="0" role="button" onClick={noop}>You have no season rosters.</a></li>);
  } else {
    listItems = seasonRosters.map(roster =>
      <li key={roster.id}><a href="TODO">{roster.name}</a></li>,
    );
  }

  return (
    <div className="dropdown">
      <a
        disabled={seasonRosters === null}
        className="btn btn-link dropdown-toggle"
        role="button"
        id={id}
        data-toggle="dropdown"
        aria-haspopup="true"
        aria-expanded="true"
      >
        Add players via season roster
        <i className="fa fa-fw fa-caret-down" />
      </a>
      {listItems !== null &&
      <ul
        className="dropdown-menu dropdown-menu-right"
        aria-labelledby={id}
      >
        {listItems}
      </ul>
      }
    </div>
  );
};

export default SeasonRosterDropdownComponent;

SeasonRosterDropdownComponent.propTypes = {
  seasonRosters: PropTypes.arrayOf(seasonRosterPropType),
  teamType: PropTypes.string.isRequired,
};

SeasonRosterDropdownComponent.defaultProps = {
  seasonRosters: null,
};
