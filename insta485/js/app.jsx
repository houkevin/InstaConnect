import React from 'react';
import PropTypes from 'prop-types';
import Posts from './posts';

class App extends React.Component {
  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = { };
  }

  componentDidMount() {
    // Call REST API to get posts
    const { url } = this.props;
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then(() => {
        this.setState({ });
      })
      .catch((error) => console.log(error));
  }

  render() {
    // render posts
    return (
      <div className="app">
        <Posts url="/api/v1/p/" />
      </div>
    );
  }
}

App.propTypes = {
  url: PropTypes.string.isRequired,
};

export default App;
