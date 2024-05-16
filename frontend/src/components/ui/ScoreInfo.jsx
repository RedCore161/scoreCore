import React from "react";
import "../ui/css/ScoreInfo.css"

const ScoreInfo = ({score}) => {

  return (
    <div>
      {Object.keys(score.data)}
    </div>
  );
};

export default ScoreInfo;
