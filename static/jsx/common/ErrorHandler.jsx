import React from 'react';
import PropTypes from 'prop-types';


export default class ErrorHandler extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      error: null,
    };
  }

  componentDidCatch(error) {
    // TODO Log to external service
    this.setState({ error });
  }

  render() {
    const { error } = this.state;
    const { children } = this.props;

    if (error) {
      return (
        <div className="text-center">
          <h3 className="text-danger">We have encountered an error.</h3>
        </div>
      );
    }
    return children;
  }
}

ErrorHandler.propTypes = {
  children: PropTypes.node.isRequired,
};

export const withErrorHandling = (Component, opts) => (
  <ErrorHandler><Component {...opts} /></ErrorHandler>
);
