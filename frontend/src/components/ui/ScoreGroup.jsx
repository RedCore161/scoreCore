import { FormCheck } from "react-bootstrap";
import React from "react";
import "../ui/css/ScoreGroup.css"

const ScoreGroup = ({callback, action}) => {

  return (
    <div key={ `inline-radio-${action}` } className="mb-3">
      <FormCheck className={"pe-4 custom-radio"} inline name={"score-group"} type={ "radio" } id={ 0 } label={ 0 } onChange={() => callback(action, "0")}/>
      <FormCheck className={"pe-4 custom-radio"} inline name={"score-group"} type={ "radio" } id={ 1 } label={ 1 } onChange={() => callback(action, "1")}/>
      <FormCheck className={"pe-4 custom-radio"} inline name={"score-group"} type={ "radio" } id={ 2 } label={ 2 } onChange={() => callback(action, "2")}/>
      <FormCheck className={"pe-4 custom-radio"} inline name={"score-group"} type={ "radio" } id={ 6 } label={ "Unclear" } onChange={() => callback(action, "X")}/>
    </div>
  );
};

export default ScoreGroup;
