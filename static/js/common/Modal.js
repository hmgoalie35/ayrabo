import React from 'react';
import PropTypes from 'prop-types';
import cn from 'classnames';


const ModalHeader = ({ modalId, title }) => (
  <div className="modal-header">
    <button
      type="button"
      className="close"
      data-dismiss="modal"
      aria-label="Close"
    >
      <span aria-hidden="true">&times;</span>
    </button>
    <h4 className="modal-title" id={`${modalId}-modal-label`}>{title}</h4>
  </div>
);

ModalHeader.propTypes = {
  modalId: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
};


const Modal = (props) => {
  const {
    size,
    id,
    title,
    children,
    footer,
  } = props;

  return (
    <div
      className="modal fade"
      id={id}
      tabIndex="-1"
      role="dialog"
      aria-labelledby={`${id}-modal-label`}
    >
      <div className={cn('modal-dialog', { [`modal-${size}`]: size })} role="document">
        <div className="modal-content">
          {title && <ModalHeader modalId={id} title={title} />}
          {children && <div className="modal-body">{children}</div>}
          {footer && <div className="modal-footer">{footer}</div>}
        </div>
      </div>
    </div>
  );
};

export default Modal;

Modal.propTypes = {
  size: PropTypes.oneOf(['sm', 'lg']),
  id: PropTypes.string.isRequired,
  title: PropTypes.string,
  children: PropTypes.node,
  footer: PropTypes.node,
};

Modal.defaultProps = {
  size: null,
  title: null,
  children: null,
  footer: null,
};
