import { Button, Col, Row } from "react-bootstrap";
import React from "react";
import "../ui/css/ProjectCardView.css";
import { useNavigate } from "react-router-dom";
import { useAuthUser } from "react-auth-kit";

const ProjectCardView = ({ id, name, features, icon, imagesTotal, uselessCount, scoresCount, scoresOwn, users,
                           wanted_scores_per_user, wanted_scores_per_image, isFinished }) => {
  let navigate = useNavigate();
  const auth = useAuthUser();
  const isAuth = auth()

  function get_score_ratio() {
    if (imagesTotal === 0){
      return 0
    }
    return Math.round(scoresCount / imagesTotal * 100) / 100
  }

  const score_ratio = get_score_ratio()

  function navigateToUselessImages() {
    if (isAuth.is_superuser) {
      navigate(`/project/${ id }/useless`)
    }
  }

  function get_save_wanted_scores() {
    return Math.min(wanted_scores_per_user, imagesTotal - uselessCount)
  }

  function get_own_percentage() {
    return Math.min(((scoresOwn / get_save_wanted_scores()) * 100), 100).toFixed(2)
  }

  const save_wanted_scores = get_save_wanted_scores()

  return (
    <Col key={ id } md={ 4 } className={"pb-4"}>
      <div className={"project-Card bg-secondary m-1"} >
        <Row>
          <Col className={`project-Card-Header ${isFinished === true ? "bg-success" : "bg-info"}`}>
            <span className={"project-Card-Header-Content"} onClick={ () => navigate(`/project/${ id }/score`) }>{ icon }{ name }</span>
            { isAuth.is_superuser && (
              <div className={"float-end"}>
                <i className="project-Card-Header-Content bi bi-patch-check" onClick={() => navigate(`/project/${ id }/investigate`)}/>&nbsp;
                <i className="project-Card-Header-Content bi bi-calculator-fill" onClick={() => navigate(`/project/${ id }/differences`)}/>
              </div>
            )}
          </Col>
        </Row>

        <Row>
          <Col md={6} className={"project-Card-Item"}>Features:</Col>
          <Col className={"project-Card-Content"}>{ features.map(ft => ft.name).join(', ') }</Col>
        </Row>
        <Row>
          <Col md={6} className={"project-Card-Item"}>Assigned Users:</Col>
          <Col className={"project-Card-Content"}>{ users.length }</Col>
        </Row>
        <Row>
          <Col md={6} className={"project-Card-Item"}>Scoreable Images:</Col>
          <Col className={"project-Card-Content"}>{ imagesTotal }</Col>
        </Row>
        <Row>
          <Col md={6} className={"project-Card-Item"}>Target Scores / User:</Col>
          <Col className={"project-Card-Content"}>{ wanted_scores_per_user }</Col>
        </Row>
        <Row>
          <Col md={6} className={"project-Card-Item"}>Target Scores / Image:</Col>
          <Col className={`project-Card-Content ${wanted_scores_per_user > save_wanted_scores && "text-warning"}`}>{ wanted_scores_per_image }</Col>
        </Row>
        <Row>
          <Col md={6} className={"project-Card-Item"}>Scores / Image:</Col>
          <Col className={`project-Card-Content ${score_ratio > 0 && score_ratio === wanted_scores_per_image && "text-success"}`}>{ score_ratio }</Col>
        </Row>
        <Row onClick={() => {navigateToUselessImages()}}>
          <Col md={6} className={"project-Card-Item"}>Useless Images:</Col>
          <Col className={`project-Card-Content ${uselessCount > 0 && "text-danger"}`}>{ uselessCount }</Col>
        </Row>
        <Row>
          <Col md={6} className={"project-Card-Item"}>
            <div>Total Score-Count:</div>
            <div>Your Score-Count:</div>
          </Col>
          <Col md={2} className={"project-Card-Content"}>
            <div>{ scoresCount }</div>
            <div className={`${scoresOwn > 0 && scoresOwn >= wanted_scores_per_user && "text-success"}`}>{ scoresOwn }</div>
          </Col>
          <Col className={"score-Info-Container"}>
            { save_wanted_scores === scoresOwn ? (
              imagesTotal > 0 && <i className="bi bi-check-lg text-success huge-icon score-Info"/>
            ) : (
              <span className={"score-Info"}>You finished:<br/> { get_own_percentage() }%</span>
            )}
          </Col>
        </Row>
      </div>
    </Col>
  );
};

export default ProjectCardView;
