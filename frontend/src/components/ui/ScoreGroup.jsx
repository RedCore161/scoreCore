import { FormCheck } from "react-bootstrap";
import React from "react";
import "../ui/css/ScoreGroup.css"
import { range } from "../../helper";

const ScoreGroup = ({callback, action, options= 3}) => {

  return (
    <div key={ `inline-radio-${action}` } className="mb-3">
      { range(0, options).map(score => {
        return <FormCheck className={"pe-4 custom-radio"} inline name={"score-group"} type={ "radio" }
                          id={ score } label={ score } onChange={() => callback(action, score)}/>
      })}
      <FormCheck className={"pe-4 custom-radio"} inline name={"score-group"} type={ "radio" }
                 id={ options + 1 } label={ "Unclear" } onChange={() => callback(action, "X")}/>
    </div>
  );
};

export default ScoreGroup;
