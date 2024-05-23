import React from "react";
import "../ui/css/ScoreInfo.css";
import ReactTimeAgo from "react-time-ago";

//  See https://dreamyguy.github.io/react-emojis/
//  🐵🐶🐱🐷🐭🐰
//  ✔⭕️❌
//  🦵🦶👂👃🦷🦴👀👅👄

const ScoreInfo = ({ score, features }) => {

  const scored = Object.values(score.data).filter(e => e).length;
  const scores = features.length;

  return (
    <div>
      { score.file_name } ({ scored } of { scores }) (<ReactTimeAgo date={ score.timestamp } locale="de-DE"/>)
      {/*{Object.keys(data)}*/ }
    </div>
  );
};

export default ScoreInfo;
