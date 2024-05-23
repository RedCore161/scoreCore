import React from "react";
import "../ui/css/ScoreInfo.css";
import ReactTimeAgo from "react-time-ago";
import { getGradiColor } from "../../helper";

//  See https://dreamyguy.github.io/react-emojis/
//  🐵🐶🐱🐷🐭🐰
//  ✔⭕️❌
//  🦵🦶👂👃🦷🦴👀👅👄

const ScoreInfo = ({ score, features }) => {

  const scored = Object.values(score.data).filter(e => e).length;
  const scores = features.length;
  const col = getGradiColor(scored, scores)

  return (
    <div style={{color: col}}>
      {score.is_completed && "✔"}{ score.file_name } ({ scored } of { scores }) (<ReactTimeAgo date={ score.timestamp } locale="en"/>)
      {/*{Object.keys(data)}*/ }
    </div>
  );
};

export default ScoreInfo;
