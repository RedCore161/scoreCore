import React from "react";
import LoginForm from "./components/auth/LoginForm";
import { WebSocketProvider } from "./components/ws/websocketContext";
import { Navigate, Route, Routes } from "react-router";
import Navbar from "./components/navbar/Navbar";
import "photoswipe/dist/photoswipe.css";

const BackupView = React.lazy(() => import("./components/main/BackupView"));
const DockerStatusView = React.lazy(() => import("./components/main/DockerStatusView"));
const IndexView = React.lazy(() => import("./components/main/IndexView"));
const UselessImageFilesView = React.lazy(() => import("./components/main/UselessImageFilesView"));
const ProjectEvaluateView = React.lazy(() => import("./components/main/ProjectEvaluateView"));
const ProjectDifferencesView = React.lazy(() => import("./components/main/ProjectDifferencesView"));
const ProjectInvestigateView = React.lazy(() => import("./components/main/ProjectInvestigateView"));
const ScoreView = React.lazy(() => import("./components/main/ScoreView"));


const CoreRoutes = () => {
  return (
    <Routes>
      {/*API-Routes*/ }
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

      <Route path={ `/login` } element={ <LoginForm /> }/>

    </Routes>
  );
};
export default CoreRoutes;
