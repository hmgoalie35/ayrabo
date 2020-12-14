import React from 'react';
import PropTypes from 'prop-types';

import Modal from '../common/Modal';
import { seasonRosterPropType } from '../common/proptypes';


const SeasonRosterModalComponent = (props) => {
  const { roster, handleAddPlayers } = props;
  const { players } = roster;
  const modalId = `modal-${roster.id}`;

  const handleAdd = () => {
    handleAddPlayers(players);
    $(`#${modalId}`).modal('hide');
  };

  const footer = (
    <React.Fragment>
      <button type="button" className="btn btn-link" data-dismiss="modal">Cancel</button>
      <button
        type="button"
        className="btn btn-success"
        onClick={handleAdd}
      >
        Add
      </button>
    </React.Fragment>
  );

  return (
    <Modal
      size="sm"
      id={modalId}
      title={`Add players from "${roster.name}"`}
      footer={footer}
    >
      <ul className="list-group">
        {players.map(player => (
          <li key={player.id} className="list-group-item list-group-item-slim">
            {`#${player.jersey_number} ${player.user.first_name} ${player.user.last_name} ${player.position}`}
          </li>
        ))}
      </ul>
    </Modal>
  );
};

export default SeasonRosterModalComponent;

SeasonRosterModalComponent.propTypes = {
  roster: seasonRosterPropType.isRequired,
  handleAddPlayers: PropTypes.func.isRequired,
};
