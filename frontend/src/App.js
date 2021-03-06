import React, { useEffect } from 'react';
import { connect, useDispatch } from 'react-redux';
import { Col, Container, Row } from "react-bootstrap";

import { BrowserRouter as Router, Navigate, Route, Routes } from 'react-router-dom';
import { SnackbarProvider } from "notistack";
import LoginForm from "./components/auth/LoginForm";
import { ModalProvider } from "./components/modal/coreModalContext";

import Navbar from "./components/navbar/Navbar";
import ScoreView from "./components/main/ScoreView";
import LoadingIcon from "./components/ui/LoadingIcon";
import IndexView from "./components/main/IndexView";
import UselessImageFilesView from "./components/main/UselessImageFilesView";
import * as actions from './store/actions/auth';
import "./style.scss";
import ProjectEvaluateView from "./components/main/ProjectEvaluateView";
import BackupView from "./components/main/BackupView";
import ProjectDifferencesView from "./components/main/ProjectDifferencesView";
import { WebSocketProvider } from "./components/ws/websocketContext";
import DockerStatusView from "./components/main/DockerStatusView";
import ProjectInvestigateView from "./components/main/ProjectInvestigateView";

const mapStateToProps = (state) => {
  return {
    isAuthenticated: !!state.token,
    isLoading: state.loading,
    error: state.error,
    is_staff: state.is_staff,
    is_superuser: state.is_superuser,
    is_active: state.is_active
  };
};

const App = props => {

  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(actions.authCheckState());
  }, []);

  return (
    <SnackbarProvider maxSnack={ 5 } anchorOrigin={ { vertical: 'top', horizontal: 'right', } }>
      <ModalProvider>
        <Container fluid>
          <Row>
            { props.isLoading ? ( <LoadingIcon /> ) : (
              !props.isAuthenticated ? (
                <Col>
                  <Router>
                    <Routes>

                      {/*Default-Route*/ }
                      <Route path="/*" element={ <LoginForm /> }/>

                    </Routes>
                  </Router>
                </Col>
              ) : (
                <>
                  <Navbar />
                  <Col md={ 10 } className={ "ps-3" }>
                    <Router>
                      <Routes>
                        {/*Authenticated-Routes*/ }
                        <Route exact path="/project/overview/" element={ <IndexView /> }/>
                        <Route exact path="/project/evaluate/" element={ <ProjectEvaluateView /> }/>
                        <Route exact path="/project/backup/" element={ <BackupView /> }/>
                        <Route exact path="/project/:id/score" element={ <ScoreView /> }/>
                        <Route exact path="/project/:id/useless" element={ <UselessImageFilesView /> }/>
                        <Route exact path="/project/:id/differences" element={ <ProjectDifferencesView /> }/>
                        <Route exact path="/project/:id/investigate" element={ <ProjectInvestigateView /> }/>
                        <Route path="/docker" element={ <WebSocketProvider url={ "/ws/docker/status" }><DockerStatusView /></WebSocketProvider> }/>


                        {/*Default-Route*/ }
                        <Route path="/*" element={ <Navigate exact from="/" to="/project/overview/"/> }/>

                      </Routes>
                    </Router>
                  </Col>
                </>
              )
            ) }
          </Row>
        </Container>
      </ModalProvider>
    </SnackbarProvider>
  );
};

export default connect(mapStateToProps, null)(App);
