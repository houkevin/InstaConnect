import React, { useEffect, useState } from "react";
import moment from "moment";
import Likes from "./Likes";
import Comments from "./Comments";

function Post(props) {
  const [age, setAge] = useState("");
  const [imgUrl, setImgUrl] = useState("");
  const [owner, setOwner] = useState("");
  const [ownerImgUrl, setOwnerImgUrl] = useState("");
  const [ownerShowUrl, setOwnerShowUrl] = useState("");
  const [postShowUrl, setPostShowUrl] = useState("");
  useEffect(() => {
    fetch(props.url, { credentials: 'same-origin' })
    .then((response) => {
      if (!response.ok) throw Error(response.statusText);
      return response.json();
    })
    .then((data) => {
      const timeNow = moment.utc(data.age).local().format();
      setAge(moment(timeNow).fromNow());
      setImgUrl(data.img_url);
      setOwner(data.owner);
      setOwnerImgUrl(data.owner_img_url);
      setOwnerShowUrl(data.owner_show_url);
      setPostShowUrl(data.post_show_url);
    })
    .catch((error) => console.log(error));
  }, []);
  const likeKey = `likes: ${props.url}`;
  const likeUrl = `${props.url}likes/`;
  const commentsUrl = `${props.url}comments/`;
  return (
    <div className="container">
      <div className="card">
        <div className="card-header">
          <div className="profile-img">
            <a href={ownerShowUrl}>
              <img src={ownerImgUrl} alt="user-pic" width="25" height="25" />
            </a>
          </div>
          <div className="profile-name">
            <a href={ownerShowUrl}>{owner}</a>
          </div>
          <div className="time">
            <a className="time" href={postShowUrl}>
              {age}
            </a>
          </div>
          <Likes url={likeUrl} imgUrl={imgUrl} key={likeKey} />
          <Comments url={commentsUrl} />
        </div>
      </div>
    </div>
  );
}

export default Post;
