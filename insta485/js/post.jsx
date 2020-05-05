import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';
import Likes from './likes';
import Comments from './comments';

class Post extends React.Component {
  constructor(props) {
    // Initialize mutable state
    super(props);

    this.state = {
      age: '',
      imgUrl: '',
      owner: '',
      ownerImgUrl: '',
      ownerShowUrl: '',
      postShowUrl: '',
    };
  }

  componentDidMount() {
    // Call REST API to get posts
    const { url } = this.props;
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        const timeNow = moment.utc(data.age).local().format();
        this.setState({
          age: moment(timeNow).fromNow(),
          imgUrl: data.img_url,
          owner: data.owner,
          ownerImgUrl: data.owner_img_url,
          ownerShowUrl: data.owner_show_url,
          postShowUrl: data.post_show_url,
        });
      })
      .catch((error) => console.log(error));
  }

  render() {
    const { url } = this.props;
    const likeKey = `likes: ${url}`;
    const likeUrl = `${url}likes/`;
    const commentsUrl = `${url}comments/`;
    const { ownerShowUrl } = this.state;
    const { postShowUrl } = this.state;
    const { owner } = this.state;
    const { imgUrl } = this.state;
    const { age } = this.state;
    const { ownerImgUrl } = this.state;
    // render a post
    return (
      <div class="container my-container">
        <div class="row my-row">
          <div class="col my-col-prof">
            <a href={ownerShowUrl}>
                <img src={ownerImgUrl} alt = ""
                width="40" height="40"/>
            </a>
            <a class="a-link" href={ownerShowUrl}>
              {owner}
            </a>
          </div>
          <div class="col my-col-prof text-right">
              <a class="a-link" href={postShowUrl}>
                {age}
              </a> 
          </div>
        </div>
        <Likes url={likeUrl} imgUrl={imgUrl} key={likeKey} />
        <Comments url={commentsUrl} />
      </div>
    );
  }
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Post;
