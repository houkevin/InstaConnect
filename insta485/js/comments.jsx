import React, { useEffect } from "react";

function Comments(props) {
  const [comments, setComments] = useState([]);
  const [value, setValue] = useState("");
  const [numComments, setNumComments] = useState(0);
  useEffect(() => {
    fetch(props.url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        const commentsVal = [];
        let commentsCount = numComments;
        data.comments.forEach((comment) => {
          commentsVal.push(
            <p key={commentsCount}>
              <a href={comment.owner_show_url}>{comment.owner}</a>
              {comment.text}
            </p>
          );
          commentsCount += 1;
        });

        setComments(commentsVal);
        setNumComments(commentsCount);
      })
      .catch((error) => console.log(error));
  }, []);
  function addCommentHandler() {
    fetch(props.url, {
      credentials: "same-origin",
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: String(value),
      }),
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        const commentsVal = [];
        commentsVal.push(
          <p key={numComments}>
            <a href={data.owner_show_url}>{data.owner}</a>
            {data.text}
          </p>
        );
        setComments(comments.concat(commentsVal));
        setValue("");
        setNumComments(numComments + 1);
      })
      .catch((error) => console.log(error));
  }
  function submitHandler(event) {
    event.preventDefault();
    if (value === "") {
      return;
    }
    addCommentHandler();
  }
  function changeHandler(event) {
    setValue(event.target.value);
  }

  return (
    <div className="comments">
      {comments}
      <form className="comment-form" onSubmit={submitHandler}>
        <input onChange={changeHandler} type="text" value={value} />
      </form>
    </div>
  );
}

export default Comments;
