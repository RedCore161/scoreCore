import React from "react";
import ReactTimeAgo from "react-time-ago";
import { getGradiColor } from "../../helper";
import { Link } from "@mui/material";
import "../ui/css/ScoreInfo.css";

//  See https://dreamyguy.github.io/react-emojis/
//  🐵🐶🐱🐷🐭🐰
//  ✔⭕️❌
//  🦵🦶👂👃🦷🦴👀👅👄
// ░▒▓
// ▄ █ ▀

const ScoreInfo = ({ project, score, features }) => {

  const scored = Object.values(score.data).filter(e => e !== undefined).length;
  const scores = features.length;
  const col = getGradiColor(scored, scores)

  return (

    <Link style={{color: col, display: "block"}}
          underline={"hover"}
          variant={"inherit"}
          href={`/project/${project}/score/?file=${score.file}`}>
      {score.is_completed ? "✔" : "⭕️"}{ score.file_name }  (<ReactTimeAgo date={ score.timestamp } locale="en"/>)
    </Link>
  );
};

export default ScoreInfo;
