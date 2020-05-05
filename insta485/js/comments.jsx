import React from 'react';
import PropTypes from 'prop-types';

class Comments extends React.Component {
  /* Display number of likes a like/unlike button for one post
   * Reference on forms https://facebook.github.io/react/docs/forms.html
   */

  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = { comments: [], value: '', numComments: 0 };
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
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
        const commentsVal = [];
        let { numComments } = this.state;
        data.comments.forEach((comment) => {
          commentsVal.push((
            <div class="row my-row" key={numComments}>
              <a class="a-link" href={comment.owner_show_url}>
              {comment.owner}
              </a>
              {comment.text}
            </div>
          ));
          numComments += 1;
        });

        this.setState({
          comments: commentsVal,
          numComments,
        });
      })
      .catch((error) => console.log(error));
  }

  handleSubmit(e) {
    e.preventDefault();
    const { value, comments } = this.state;
    const { url } = this.props;
    // simple check to prevent empty comments
    if (value === '') {
      return;
    }
    fetch(url, {
      credentials: 'same-origin',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: String(value),
      }),
    }).then((response) => {
      if (!response.ok) throw Error(response.statusText);
      return response.json();
    })
      .then((data) => {
        let { numComments } = this.state;
        const commentsVal = [];
        commentsVal.push(
          <div class="row my-row" key={numComments}>
              <a class="a-link" href={data.owner_show_url}>
                {data.owner}
              </a>
              {data.text}
          </div>
        );

        numComments += 1;

        this.setState({
          comments: comments.concat(commentsVal),
          value: '',
          numComments,
        });
      })
      .catch((error) => console.log(error));
  }

  handleChange(e) {
    // Handle add comment.
    this.setState((
      {
        value: e.target.value,
      }
    ));
  }

  render() {
    // Render number of likes
    const { comments } = this.state;
    const { value } = this.state;
    return (
      <div className="comments">
        {comments}
        <div class="row my-row">
          <form className="comment-form" onSubmit={this.handleSubmit}>
            <input
              onChange={this.handleChange}
              type="text"
              value={value}
            />
          </form>
        </div>
      </div>
    );
  }
}

Comments.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Comments;
