import React, { useState, useEffect } from "react";
import Post from "./Post";

function Posts(props) {
  const [output, setOutput] = useState([]);
  useEffect(() => {
      fetch(props.url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        const outputVals = [];
        data.results.forEach((result) => {
          outputVals.push(<Post url={result.url} key={result.url} />);
        });
        setOutput(outputVals);
      })
      .catch((error) => console.log(error));
  }, []);

  return (
      <div>
          {output}
      </div>
  )
}
export default Posts;
