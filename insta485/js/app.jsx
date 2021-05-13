import React from "react";
import Posts from './Posts'

function App(props) {
  const newUrl = props.url + "p/";
  return (
    <div>
      <Posts url={newUrl}/>
    </div>
  );
}

export default App;
