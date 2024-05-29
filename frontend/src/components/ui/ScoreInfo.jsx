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

const ScoreInfo = ({ images, score }) => {

  const scored = Object.values(score.data).filter(e => e !== undefined).length;
  const scores = images.features.length;
  // const col = getGradiColor(scored, scores)

  return (
    // color: col,
    <Link style={{display: "block"}}
          underline={"hover"}
          // variant={"inherit"}
          href={`/project/${images.image.project}/score/?file=${score.file}`}>
      {score.is_completed ? "✔" : "⭕️"}{ score.file_name }  (<ReactTimeAgo date={ score.timestamp } locale="en"/>)
    </Link>
  );
};

export default ScoreInfo;
