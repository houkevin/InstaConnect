import React, { useEffect, useState } from "react";

function Likes(props) {
  const [numLikes, setNumLikes] = useState(0);
  const [lognameLikesThis, setLogNameLikesThis] = useState(false);
  const [likeBtnTxt, setLikeBtnTxt] = useState("");
  useEffect(() => {
    fetch(props.url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        setNumLikes(data.likes_count);
        setLogNameLikesThis(data.logname_likes_this);
      })
      .catch((error) => console.log(error));
  }, []);
  function likeUnlikeHandler() {
    if (lognameLikesThis === 1) {
      fetch(props.url, { credentials: "same-origin", method: "DELETE" })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
        })
        .then(() => {
          setNumLikes(numLikes - 1);
          setLogNameLikesThis(false);
          setLikeBtnTxt("unlike");
        })
        .catch((error) => console.log(error));
    } else {
      likeHandler();
    }
  }

  function likeHandler() {
    fetch(props.url, { credentials: "same-origin", method: "POST" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
      })

      .then(() => {
        setNumLikes(numLikes + 1);
        setLogNameLikesThis(true);
        setLikeBtnTxt("like");
      })
      .catch((error) => console.log(error));
  }

  function handleDoubleClick() {
    if (lognameLikesThis === 0) {
      likeHandler();
    }
  }

  return (
    <div className="likes">
      <div className="content-img">
        <img
          src={imgUrl}
          alt="user-post"
          className="post-img"
          onDoubleClick={handleDoubleClick}
        />
      </div>
      <button
        className="like-unlike-button"
        onClick={likeUnlikeHandler}
        type="submit"
      >
        {likeBtnTxt}
      </button>
      <p>
        {numLikes} like
        {numLikes !== 1 ? "s" : ""}
      </p>
    </div>
  );
}

export default Likes;
