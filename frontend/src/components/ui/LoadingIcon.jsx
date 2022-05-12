import { Col } from "react-bootstrap";
import React from "react";
import { RotatingLines } from "react-loader-spinner";
import "../ui/css/LoadingIcon.css"

const LoadingIcon = () => {

  return (
    <Col className={"loadingIcon text-center"}>
      <RotatingLines width="100" />
    </Col>
  );
};

export default LoadingIcon;
