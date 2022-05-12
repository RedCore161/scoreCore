import React, { Component, useEffect } from 'react';
import { connect, useDispatch } from 'react-redux';
import { Col, Container, Row } from "react-bootstrap";

import { BrowserRouter as Router, Navigate, Route, Routes } from 'react-router-dom';
import { SnackbarProvider } from "notistack";
import LoginForm from "./components/auth/LoginForm";
import { ModalProvider } from "./components/modal/coreModalContext";

import Navbar from "./components/navbar/Navbar";
import ScoreView from "./components/main/ScoreView";

import * as actions from './store/actions/auth';

import "./style.scss";
import LoadingIcon from "./components/ui/LoadingIcon";
import IndexView from "./components/main/IndexView";
import { WebSocketProvider } from "./components/ws/websocketContext";
import UselessImageFilesView from "./components/main/UselessImageFilesView";


const mapStateToProps = state => {
  return {
    isAuthenticated: state.token !== null,
    isLoading: state.loading
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
                  <Navbar dispatch={ dispatch }/>
                  <Col md={ 10 } className={ "ps-3" }>
                    <Router>
                      <Routes>
                        {/*Authenticated-Routes*/ }
                        <Route exact path="/project/overview/" element={ <IndexView /> }/>
                        <Route exact path="/project/:id/score" element={ <ScoreView /> }/>
                        <Route exact path="/project/:id/useless" element={ <UselessImageFilesView /> }/>
                        {/*<Route exact path="/stack/" element={ <WebSocketProvider url={ "/ws/stack/" }><StackTestsView /></WebSocketProvider> }/>*/ }
                        {/*<Route exact path="/app/" element={ <WebSocketProvider url={ "/ws/product/test/" }><AppTestsView /></WebSocketProvider> }/>*/ }
                        {/*<Route exact path="/app/:product/:version" element={ <WebSocketProvider url={ "/ws/product/test/" }><AppAllTestsView /></WebSocketProvider> }/>*/ }
                        {/*<Route exact path="/app/viewer" element={ <AppTestRecordView /> }/>*/ }
                        {/*<Route exact path="/app/fix" element={ <AppTestsFixxer /> }/>*/ }

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
