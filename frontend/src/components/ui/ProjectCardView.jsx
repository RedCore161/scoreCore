import { Col, Row } from "react-bootstrap";
import React from "react";
import "../ui/css/ProjectCardView.css";
import { useNavigate } from "react-router-dom";
import { useAuthHeader, useAuthUser } from "react-auth-kit";
import axiosConfig from "../../axiosConfig";


const ProjectCardView = ({ id, name, features, icon, data, users,
                           wanted_scores_per_user, wanted_scores_per_image, isFinished }) => {

  const navigate = useNavigate();
  const auth = useAuthUser();
  const isAuth = auth();
  const authHeader = useAuthHeader();

  const { imagesTotal, scoresCount, scoresOwn, uselessCount } = data

  const save_wanted_scores = get_save_wanted_scores();

  function get_score_ratio() {
    if (imagesTotal === 0) {
      return 0;
    }
    return Math.round(scoresCount / imagesTotal * 100) / 100;
  }

  const score_ratio = get_score_ratio();

  function navigateToUselessImages() {
    if (isAuth.is_superuser) {
      navigate(`/project/${ id }/useless`);
    }
  }

  function get_save_wanted_scores() {
    return Math.min(wanted_scores_per_user, imagesTotal - uselessCount);
  }

  function get_own_percentage() {
    return Math.min(( ( scoresOwn / get_save_wanted_scores() ) * 100 ), 100).toFixed(2);
  }

  function get_project_percentage() {
    return Math.min(( ( scoresCount / ( users.length * wanted_scores_per_user) ) * 100 ), 100).toFixed(2);
  }

  function loginForwardTo(event, url) {
    event.stopPropagation();

    const _header = authHeader();
    axiosConfig.updateToken(_header);
    axiosConfig.holder.post(`/api/user/login/`, { token: _header.substring(7) }).then((response) => {
      if (response.data.success) {
        window.open(url, "_blank");
      }
    }, (error) => {
      if (error.response) {
        console.log(error.response.data);
      } else {
        console.error(error);
      }
    });
  }

  function openHeatMap(event) {
    event.stopPropagation();

    const _header = authHeader();
    axiosConfig.updateToken(_header);
    axiosConfig.holder.get(`/api/project/${id}/cross-stddev-all/`, { responseType: "blob"}).then((response) => {
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const newTab = window.open();
      newTab.location = url;
    }, (error) => {
      if (error.response) {
        console.log(error.response.data);
      } else {
        console.error(error);
      }
    });
  }

  function advNavigate(event, url) {
    event.stopPropagation();
    navigate(url);
  }

  async function readImages(event) {
    event.stopPropagation();
    axiosConfig.updateToken(authHeader());
    await axiosConfig.holder.get(`/api/project/${ id }/read-images/`).then((response) => {
      if (response.data.success) {
        window.location.reload(true);
      }
    }, (error) => {
      if (error.response) {
        console.error(error.response.data);
      } else {
        console.error(error);
      }
    });
  }

  return (
    <Col key={ id } md={ 4 } className={ "pb-4" }>
      <div className={ "project-Card bg-secondary m-1 h-100" }>
        <Row>
          <Col className={ `project-Card-Header ${ isFinished ? "bg-success" : "bg-info" }` }
               onClick={ (e) => advNavigate(e, `/project/${ id }/score`) }>
            <span className={ "project-Card-Header-Content" }>{ icon }{ name }</span>
            { isAuth.is_superuser && (
              <div className={ "float-end" }>
                <span className="project-Card-Header-Content me-2" onClick={(e) => openHeatMap(e)}>🔥</span>
                <i className="project-Card-Header-Content bi bi-pencil-fill me-2"
                   onClick={ (e) => loginForwardTo(e, `${ process.env.REACT_APP_BACKEND_URL }/admin/scoring/project/${ id }/change/`) }/>
                <i className="project-Card-Header-Content bi bi-arrow-repeat me-2" onClick={ (e) => readImages(e) }/>
                <i className="project-Card-Header-Content bi bi-patch-check me-2"
                   onClick={ (e) => advNavigate(e, `/project/${ id }/investigate`) }/>
                <i className="project-Card-Header-Content bi bi-calculator-fill me-2"
                   onClick={ (e) => advNavigate(e, `/project/${ id }/differences`) }/>
              </div>
            ) }
          </Col>
        </Row>

        <Row className={"pt-2"}>
          <Col md={ 6 } className={ "project-Card-Item" }>Features:</Col>
          <Col className={ "project-Card-Content" }>{ features.map(ft => ft.name).join(', ') }</Col>
        </Row>
        <Row>
          <Col md={ 6 } className={ "project-Card-Item" }>Assigned Users:</Col>
          <Col className={ "project-Card-Content" }>{ users.length }</Col>
        </Row>
        <Row>
          <Col md={ 6 } className={ "project-Card-Item" }>Scoreable Images:</Col>
          <Col className={ "project-Card-Content" }>{ imagesTotal }</Col>
        </Row>
        <Row>
          <Col md={ 6 } className={ "project-Card-Item" }>
            <div>Target Scores / User:</div>
            <div>Target Scores / Image:</div>
          </Col>
          <Col md={ 2 } className={ "project-Card-Content" }>
            <div className={ wanted_scores_per_user > save_wanted_scores ? "text-warning" : ""}>{ wanted_scores_per_user }</div>
            <div>{ wanted_scores_per_image }</div>
          </Col>
          <Col className={ "score-Info-Container" }>
            <span className={ "score-Info" }>Project finished:<br/> { get_project_percentage() }%</span>
          </Col>
        </Row>

        <Row>
          <Col md={ 6 } className={ "project-Card-Item" }>Scores / Image:</Col>
          <Col
            className={ `project-Card-Content ${ score_ratio > 0 && score_ratio === wanted_scores_per_image && "text-success" }` }>{ score_ratio }</Col>
        </Row>
        <Row onClick={ () => navigateToUselessImages() }>
          <Col md={ 6 } className={ "project-Card-Item" }>Useless Images:</Col>
          <Col className={ `project-Card-Content ${ uselessCount > 0 && "text-danger" }` }>{ uselessCount }</Col>
        </Row>

        <Row>
          <Col md={ 6 } className={ "project-Card-Item" }>
            <div>Total Score-Count:</div>
            <div>Your Score-Count:</div>
          </Col>
          <Col md={ 2 } className={ "project-Card-Content" }>
            <div>{ scoresCount }</div>
            <div className={ `${ scoresOwn > 0 && scoresOwn >= wanted_scores_per_user && "text-success" }` }>
              { scoresOwn }</div>
          </Col>
          <Col className={ "score-Info-Container" }>
            { save_wanted_scores === scoresOwn ? (
              imagesTotal > 0 && <i className="bi bi-check-lg text-success huge-icon score-Info"/>
            ) : (
              <span className={ "score-Info" }>Your part finished:<br/> { get_own_percentage() }%</span>
            ) }
          </Col>
        </Row>
      </div>
    </Col>
  );
};
export default ProjectCardView;
