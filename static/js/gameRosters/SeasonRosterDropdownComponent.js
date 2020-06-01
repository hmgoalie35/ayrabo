/* eslint-disable jsx-a11y/anchor-is-valid,jsx-a11y/click-events-have-key-events */
import React from 'react';
import PropTypes from 'prop-types';
import { noop } from 'lodash/util';
import cn from 'classnames';
import { seasonRosterPropType } from '../common/proptypes';
import SeasonRosterModalComponent from './SeasonRosterModalComponent';


const SeasonRosterDropdownComponent = (props) => {
  const { teamType, seasonRosters, handleAddPlayers } = props;
  const id = `season-roster-${teamType}`;
  let listItems = null;
  let seasonRosterModals = null;

  if (seasonRosters === null) {
    listItems = null;
    seasonRosterModals = null;
  } else if (seasonRosters.length === 0) {
    listItems = (
      <li><a tabIndex="0" role="button" onClick={noop}>There are no season rosters.</a></li>
    );
  } else {
    listItems = seasonRosters.map(roster => (
      <li key={roster.id}>
        <a data-toggle="modal" data-target={`#modal-${roster.id}`} role="button">{roster.name}</a>
      </li>
    ));
    seasonRosterModals = seasonRosters.map(roster => (
      <div className="text-left" key={roster.id}>
        <SeasonRosterModalComponent roster={roster} handleAddPlayers={handleAddPlayers} />
      </div>
    ));
  }

  const disabled = seasonRosters === null;

  return (
    <div className="dropdown">
      <a
        disabled={disabled}
        className={cn('btn btn-link dropdown-toggle', { disabled })}
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
      <React.Fragment>
        <ul
          className="dropdown-menu dropdown-menu-right"
          aria-labelledby={id}
        >
          {listItems}
        </ul>
        {seasonRosterModals}
      </React.Fragment>
      }
    </div>
  );
};

export default SeasonRosterDropdownComponent;

SeasonRosterDropdownComponent.propTypes = {
  seasonRosters: PropTypes.arrayOf(seasonRosterPropType),
  teamType: PropTypes.string.isRequired,
  handleAddPlayers: PropTypes.func.isRequired,
};

SeasonRosterDropdownComponent.defaultProps = {
  seasonRosters: null,
};
