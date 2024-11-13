import React from "react";
import LoginForm from "./components/auth/LoginForm";
import { WebSocketProvider } from "./components/ws/websocketContext";

import BackupView from "./components/main/BackupView";
import DockerStatusView from "./components/main/DockerStatusView";
import { Navigate, Route, Routes } from "react-router-dom";
import IndexView from "./components/main/IndexView";
import UselessImageFilesView from "./components/main/UselessImageFilesView";
import ProjectEvaluateView from "./components/main/ProjectEvaluateView";
import ProjectDifferencesView from "./components/main/ProjectDifferencesView";
import ProjectInvestigateView from "./components/main/ProjectInvestigateView";
import Navbar from "./components/navbar/Navbar";
import ScoreView from "./components/main/ScoreView";
import { useLocation } from "react-router";

import AuthOutlet from '@auth-kit/react-router/AuthOutlet';

import "photoswipe/dist/photoswipe.css";

const CoreRoutes = () => {
  const location = useLocation();
  return (
    <Routes>
      {/*API-Routes*/ }
      <Route element={<AuthOutlet fallbackPath={`/login?forward=${location.pathname}`} />} >
          <Route exact path="/project/overview/" element={ <Navbar act={"overview"} content={ <IndexView /> }/>}/>
          <Route exact path="/project/evaluate/" element={ <Navbar act={"evaluate"} content={ <ProjectEvaluateView /> }/>} />
          <Route exact path="/project/backup/" element={ <Navbar act={"backup"} content={ <BackupView /> }/>} />
          <Route path="/project/:id/score" element={ <Navbar act={"score"} content={ <ScoreView /> }/>} />
          <Route path="/project/:id/useless" element={ <Navbar act={"useless"} content={ <UselessImageFilesView /> }/>} />
          <Route path="/project/:id/differences" element={ <Navbar act={"differences"} content={ <ProjectDifferencesView /> }/>} />
          <Route path="/project/:id/investigate" element={ <Navbar act={"investigate"} content={ <ProjectInvestigateView /> }/>} />
          <Route path="/docker" element={ <Navbar act={""} content={ <WebSocketProvider url={ "/ws/docker/status" }><DockerStatusView /></WebSocketProvider> }/> }/>

          {/*Default-Route*/ }
          <Route path="/*" element={ <Navigate exact from="/" to="/project/overview/"/> } />

      </Route>

      <Route path={ `/login` } element={ <LoginForm/> }/>
      <Route path="*" element={ <LoginForm/> }/>

    </Routes>
  );
};
export default CoreRoutes;
