import React from 'react';
import PropTypes from 'prop-types';

import InfiniteScroll from 'react-infinite-scroll-component';
import Post from './post';

class Posts extends React.Component {
  constructor(props) {
    // Initialize mutable state
    super(props);

    this.state = { next: '', output: [] };
    this.fetchMoreData = this.fetchMoreData.bind(this);
  }

  componentDidMount() {
    if (performance.navigation.type === PerformanceNavigation.TYPE_BACK_FORWARD) {
      const output = JSON.parse(window.history.state.output);
      const outputVals = [];

      output.forEach((post) => {
        outputVals.push(<Post url={post.props.url} key={post.key} />);
      });

      this.setState({
        next: window.history.state.next,
        output: outputVals,
      });
    } else {
      const { url } = this.props;
      fetch(url, { credentials: 'same-origin' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          const outputVals = [];
          data.results.forEach((result) => {
            outputVals.push(<Post url={result.url} key={result.url} />);
          });
          this.setState({
            next: data.next,
            output: outputVals,
          });
        })
        .catch((error) => console.log(error));
    }
  }

  fetchMoreData() {
    const { next } = this.state;
    const { output } = this.state;
    if (next === '') {
      console.log('no more posts to load');
      return;
    }

    fetch(next, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        const outputVals = [];
        data.results.forEach((result) => {
          outputVals.push(<Post url={result.url} key={result.url} />);
        });
        setTimeout(() => {
          this.setState({
            next: data.next,
            output: output.concat(outputVals),
          });
        }, 0);
        const outputJson = JSON.stringify(output.concat(outputVals));
        window.history.replaceState({ next: data.next, output: outputJson }, '');
      })
      .catch((error) => console.log(error));
  }

  render() {
    let hasMore = true;
    const { next } = this.state;
    const { output } = this.state;
    if (next === '') {
      hasMore = false;
    }
    return (
      <div className="posts">
        <InfiniteScroll
          dataLength={output.length}
          next={this.fetchMoreData}
          hasMore={hasMore}
          loader={<div className="loader" key={0}>Loading... </div>}
        >
          {output}
        </InfiniteScroll>
      </div>
    );
  }
}

Posts.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Posts;
