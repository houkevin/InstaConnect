import React from 'react';
import PropTypes from 'prop-types';

class Likes extends React.Component {
  /* Display number of likes a like/unlike button for one post
   * Reference on forms https://facebook.github.io/react/docs/forms.html
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = { numLikes: 0, lognameLikesThis: false, width: 98, height: 30};
    this.likeUnlike = this.likeUnlike.bind(this);
    this.handleDoubleClick = this.handleDoubleClick.bind(this);
  }

  componentDidMount() {
    // Call REST API to get number of likes
    const { url } = this.props;
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState({
          numLikes: data.likes_count,
          lognameLikesThis: data.logname_likes_this,
        });
      })
      .catch((error) => console.log(error));
  }

  likeUnlike() {
    const { lognameLikesThis } = this.state;
    const { numLikes } = this.state;
    if (lognameLikesThis === 1) {
      // send a unlike request
      const { url } = this.props;
      fetch(url, { credentials: 'same-origin', method: 'DELETE' })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
        })
        .then(() => {
          const likes = numLikes - 1;
          this.setState({
            numLikes: likes,
            lognameLikesThis: 0,
          });
        })
        .catch((error) => console.log(error));
    } else {
      this.likePost();
    }
  }

  handleDoubleClick() {
    const { lognameLikesThis } = this.state;
    if (lognameLikesThis === 0) {
      this.likePost();
    }
  }

  likePost() {
    const { url } = this.props;
    const { numLikes } = this.state;
    fetch(url, { credentials: 'same-origin', method: 'POST' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
      })

      .then(() => {
        const likes = numLikes + 1;
        this.setState({
          numLikes: likes,
          lognameLikesThis: 1,
        });
      })
      .catch((error) => console.log(error));
  }

  render() {
    const { lognameLikesThis } = this.state;
    const { imgUrl } = this.props;
    const { numLikes } = this.state;
    let likeBtnTxt = '';
    if (lognameLikesThis === 1) {
      likeBtnTxt = 'unlike';
    } else {
      likeBtnTxt = 'like';
    }
    // Render number of likes
    return (
      <div class="likes">
        <div class="row my-row-pic">
            <img src={imgUrl}
                alt="user-post"
                className="post-img"
                width="98%"
                height="30%"
                onDoubleClick={this.handleDoubleClick}
                />
        </div>
        <div class="row my-row">
            <button
            className="like-unlike-button"
            ref={this.myButton}
            onClick={this.likeUnlike}
            type="submit"
            >
            {likeBtnTxt}
            </button>
        </div>
        <div class="row my-row">
            {numLikes}
              {' '}
              like
              {numLikes !== 1 ? 's' : ''}
        </div>
      </div>
    );
  }
}

Likes.propTypes = {
  url: PropTypes.string.isRequired,
  imgUrl: PropTypes.string.isRequired,
};

export default Likes;
