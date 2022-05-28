import { Col, Row } from "react-bootstrap";
import React from "react";
import "../ui/css/ProjectCardView.css";
import { useNavigate } from "react-router-dom";

const ProjectCardView = ({ id, name, imagesTotal, uselessCount, scoresCount, scoresOwn, users,
                           wanted_scores_per_user, wanted_scores_per_image, isFinished }) => {
  let navigate = useNavigate();
  const isAdmin = localStorage.getItem("is_staff")

  function get_score_ratio() {
    if (imagesTotal === 0){
      return 0
    }
    return Math.round(scoresCount / imagesTotal * 100) / 100
  }

  const score_ratio = get_score_ratio()

  function navigateToUselessImages() {
    if (isAdmin === "true") {
      navigate(`/project/${ id }/useless`)
    }
  }

  return (
    <Col key={ id } md={ 4 } className={"pb-4"}>
      <div className={"project-Card bg-secondary m-1"} >
        <Row>
          <Col className={`project-Card-Header ${isFinished === true ? "bg-success" : "bg-info"}`}>
            <i className={"project-Card-Header-Content"} onClick={ () => navigate(`/project/${ id }/score`) }>{ name }</i>
            { isAdmin === "true" && (
              <div className={"float-end"}>
                <i className="project-Card-Header-Content bi bi-patch-check" onClick={() => navigate(`/project/${ id }/investigate`)}/>&nbsp;
                <i className="project-Card-Header-Content bi bi-calculator-fill" onClick={() => navigate(`/project/${ id }/differences`)}/>
              </div>
            )}
          </Col>
        </Row>
        <Row className={"pt-2"}>
          <Col md={9}>
            <Row>
              <Col md={8} className={"project-Card-Item"}>Assigned Users:</Col>
              <Col className={"project-Card-Content"}>{ users.length }</Col>
            </Row>
            <Row>
              <Col md={8} className={"project-Card-Item"}>Scoreable Images:</Col>
              <Col className={"project-Card-Content"}>{ imagesTotal }</Col>
            </Row>
            <Row>
              <Col md={8} className={"project-Card-Item"}>Target Scores / User:</Col>
              <Col className={"project-Card-Content"}>{ wanted_scores_per_user }</Col>
            </Row>
            <Row>
              <Col md={8} className={"project-Card-Item"}>Target Scores / Image:</Col>
              <Col className={"project-Card-Content"}>{ wanted_scores_per_image }</Col>
            </Row>
            <Row>
              <Col md={8} className={"project-Card-Item"}>Scores / Image:</Col>
              <Col className={`project-Card-Content ${score_ratio > 0 && score_ratio === wanted_scores_per_image && "text-success"}`}>{ score_ratio }</Col>
            </Row>
            <Row onClick={() => {navigateToUselessImages()}}>
              <Col md={8} className={"project-Card-Item"}>Useless Images:</Col>
              <Col className={`project-Card-Content ${uselessCount > 0 && "text-danger"}`}>{ uselessCount }</Col>
            </Row>
            <Row>
              <Col md={8} className={"project-Card-Item"}>Total Score-Count:</Col>
              <Col className={"project-Card-Content"}>{ scoresCount }</Col>
            </Row>

            <Row>
              <Col md={8} className={"project-Card-Item"}>Your Score-Count:</Col>
              <Col className={`project-Card-Content ${scoresOwn > 0 && scoresOwn >= wanted_scores_per_user && "text-success"}`}>{ scoresOwn }</Col>
            </Row>
          </Col>
          <Col className={"score-Info-Container"}>
            { wanted_scores_per_user === scoresOwn ? (
              imagesTotal > 0 && <i className="bi bi-check-lg text-success huge-icon score-Info"/>
            ) : (
              <span className={"score-Info"}>You finished:<br/> {Math.min(((scoresOwn / wanted_scores_per_user) * 100), 100).toFixed(2)}%</span>
            )}
          </Col>
        </Row>
      </div>
    </Col>
  );
};

export default ProjectCardView;
