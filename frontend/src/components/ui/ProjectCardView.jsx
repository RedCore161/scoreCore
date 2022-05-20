import { Button, Col, Row } from "react-bootstrap";
import React, { useState } from "react";
import "../ui/css/ProjectCardView.css";
import { useNavigate } from "react-router-dom";

const ProjectCardView = ({ id, name, imagesTotal, uselessCount, scoresCount, scoresOwn, users }) => {
  let navigate = useNavigate();
  const isAdmin = localStorage.getItem("is_staff")

  return (
    <Col key={ id } md={ 4 } className={"pb-4"}>
      <div className={"project-Card bg-secondary m-1"} >
        <Row>
          <Col className={`project-Card-Header bg-info`}>
            <i className={"project-Card-Header-Content"} onClick={ () => navigate(`/project/${ id }/score`) }>{ name }</i>
            { isAdmin === "true" && (
              <div className={"float-end"}>
                <i className="project-Card-Header-Content bi bi-clipboard-x-fill p-1" onClick={() => navigate(`/project/${ id }/useless`)}/>
                <i className="project-Card-Header-Content bi bi-calculator-fill" onClick={() => navigate(`/project/${ id }/kappa`)}/>
              </div>
            )}
          </Col>
        </Row>
        <Row className={"pt-2"}>
          <Col md={8}>
            <Row>
              <Col md={7} className={"project-Card-Item"}>Assigned Users:</Col>
              <Col md={3} className={"project-Card-Content"}>{ users.length }</Col>
            </Row>
            <Row>
              <Col md={7} className={"project-Card-Item"}>Scoreable Images:</Col>
              <Col md={3} className={"project-Card-Content"}>{ imagesTotal }</Col>
            </Row>
            <Row>
              <Col md={7} className={"project-Card-Item"}>Useless Images:</Col>
              <Col md={3} className={"project-Card-Content"}>{ uselessCount }</Col>
            </Row>
            <Row>
              <Col md={7} className={"project-Card-Item"}>Total Score-Count:</Col>
              <Col md={3} className={"project-Card-Content"}>{ scoresCount }</Col>
            </Row>
            <Row>
              <Col md={7} className={"project-Card-Item"}>Your Score-Count:</Col>
              <Col md={3} className={"project-Card-Content"}>{ scoresOwn }</Col>
            </Row>
          </Col>
          <Col className={"score-Info-Container"}>
            { imagesTotal === scoresOwn ? (
              imagesTotal > 0 && <i className="bi bi-check-lg text-success huge-icon score-Info"/>
            ) : (
              <span className={"score-Info"}>You finished:<br/> {((scoresOwn / imagesTotal) * 100).toFixed(2)}%</span>
            )}
          </Col>
        </Row>
      </div>
    </Col>
  );
};

export default ProjectCardView;
