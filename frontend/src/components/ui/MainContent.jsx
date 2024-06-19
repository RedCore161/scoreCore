import { Col } from "react-bootstrap";
import React from "react";
import { WebSocketProvider } from "../ws/websocketContext";
import BackupView from "../main/BackupView";
import DockerStatusView from "../main/DockerStatusView";
import LoginForm from "../auth/LoginForm";
import { RequireAuth, useAuthHeader } from "react-auth-kit";
import { Navigate, Route, Routes } from "react-router-dom";
import IndexView from "../main/IndexView";
import UselessImageFilesView from "../main/UselessImageFilesView";
import ProjectEvaluateView from "../main/ProjectEvaluateView";
import ProjectDifferencesView from "../main/ProjectDifferencesView";
import ProjectInvestigateView from "../main/ProjectInvestigateView";
import Navbar from "../navbar/Navbar";
import ScoreView from "../main/ScoreView";
import { useLocation } from "react-router";

import "./css/MainContent.css";
import "photoswipe/dist/photoswipe.css";

const MainContent = () => {

  const authHeader = useAuthHeader();
  const location = useLocation();

  if (authHeader()) {
    return <>
      <Navbar />
      <Col className={ "ps-2" }>
        <Routes>
          {/*Authenticated-Routes*/ }
          <Route exact path="/project/overview/" element={ <RequireAuth loginPath={ `/login?forward=${ location.pathname }` }>
            <IndexView />
          </RequireAuth> }/>
          <Route exact path="/project/evaluate/" element={ <RequireAuth loginPath={ `/login?forward=${ location.pathname }` }>
            <ProjectEvaluateView />
          </RequireAuth> }/>
          <Route exact path="/project/backup/" element={ <RequireAuth loginPath={ `/login?forward=${ location.pathname }` }>
            <BackupView />
          </RequireAuth> }/>
          <Route exact path="/project/:id/score" element={ <RequireAuth loginPath={ `/login?forward=${ location.pathname }` }>
            <ScoreView />
          </RequireAuth> }/>
          <Route exact path="/project/:id/useless" element={ <RequireAuth loginPath={ `/login?forward=${ location.pathname }` }>
            <UselessImageFilesView />
          </RequireAuth> }/>
          <Route exact path="/project/:id/differences" element={ <RequireAuth loginPath={ `/login?forward=${ location.pathname }` }>
            <ProjectDifferencesView />
          </RequireAuth> }/>
          <Route exact path="/project/:id/investigate" element={ <RequireAuth loginPath={ `/login?forward=${ location.pathname }` }>
            <ProjectInvestigateView />
          </RequireAuth> }/>
          <Route path="/docker" element={ <WebSocketProvider url={ "/ws/docker/status" }><DockerStatusView /></WebSocketProvider> }/>

          {/*Default-Route*/ }
          <Route path="/*" element={ <Navigate exact from="/" to="/project/overview/"/> }/>

        </Routes>
      </Col>
    </>
  }

  return <Routes>
    <Route path={`/login`} element={ <LoginForm /> }/>
    <Route path="/*" element={ <Navigate exact from="/" to={`/login?forward=${location.pathname}`}/> }/>
  </Routes>

};
export default MainContent;
