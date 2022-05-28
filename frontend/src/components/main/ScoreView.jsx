import React, { useLayoutEffect, useReducer, useState } from "react";
import { defaultStateScore, reducerScore } from "../reducer/reducerScore";
import { Form, Button, ButtonGroup, Col, Row } from "react-bootstrap";
import useWindowSize from 'react-use/lib/useWindowSize';
import Confetti from 'react-confetti';
import { showErrorBar, showSuccessBar } from "../ui/Snackbar";
import { useSnackbar } from "notistack";
import { useParams } from "react-router";
import { fetchImage } from "../../helper";
import LoadingIcon from "../ui/LoadingIcon";
import ScoreGroup from "../ui/ScoreGroup";
import * as actionTypes from "../reducer/reducerTypes";
import axiosConfig from "../../axiosConfig";

const ScoreView = () => {

  const { id } = useParams();
  const [images, setImages] = useState({"files_left": 0});
  const [loadingDone, setLoadingDone] = useState(false);
  const [uilock, setUILock] = useState(false);
  const [updateUi, setUpdateUi] = useState(false);
  const [state, dispatch] = useReducer(reducerScore, defaultStateScore);
  const { enqueueSnackbar } = useSnackbar();
  const { width, height } = useWindowSize();

  const actions = ["eye", "nose", "cheek", "ear", "whiskers"];

  useLayoutEffect(() => {
    console.log("fetchData");
    fetchImage(id).then((data) => {
      setImages(data);
      setLoadingDone(true);
    });

  }, []);


  const selectCallback = (action, value) => {
    dispatch({ type: actionTypes.SET_SCORE, payload: { "action": action, "value": value } });
  };

  async function confirmScore() {
    let image = images.image;
    if (uilock) {
      showErrorBar(enqueueSnackbar, "Another request isn't finished yet...");
      return;
    }
    setUILock(true);
    await axiosConfig.holder.post(`/api/imagescore/${ image.id }/confirm/`, {
      'eye': state.eye,
      'nose': state.nose,
      'cheek': state.cheek,
      'ear': state.ear,
      'whiskers': state.whiskers,
      'comment': state.comment,
      'project': id,
    }).then((response) => {
      setUILock(false);
      if (response.data) {
        if (response.data.success) {
          showSuccessBar(enqueueSnackbar, "Scoring confirmed!");
          setImages(response.data);
          dispatch({ type: actionTypes.SET_RESET });
        } else {
          if (response.data.is_finished) {
            showErrorBar(enqueueSnackbar, "Project is already finished!");
          }
        }
      } else {
        showErrorBar(enqueueSnackbar, "Couldn't confirm Score!");
      }
    }, (error) => {
      if (error.response) {
        console.error(error.response.data);
      } else {
        console.error(error);
      }
    });
  }

  async function markAsUseless() {
    let image = images.image;
    if (uilock) {
      showErrorBar(enqueueSnackbar, "Another request isn't finished yet...");
      return;
    }
    setUILock(true);
    await axiosConfig.holder.post(`/api/imagescore/${ image.id }/useless/`, {
      "project": id
    }).then((response) => {
      setUILock(false);
      if (response.data) {
        if (response.data.success) {
          showSuccessBar(enqueueSnackbar, "Image marked as Useless!");
          setImages(response.data);
          setUpdateUi(!updateUi);
          dispatch({ type: actionTypes.SET_RESET });
        }
      } else {
        showErrorBar(enqueueSnackbar, "Couldn't mark Image!");
      }
    }, (error) => {
      if (error.response) {
        console.error(error.response.data);
      } else {
        console.error(error);
      }
    });
  }

  function getImathPath() {
    return [process.env.REACT_APP_BACKEND_URL, "media", images.image.rel_path, images.image.filename].join("/");
  }

  function changeCommentListener(event) {
    dispatch({ type: actionTypes.SET_COMMENT, payload: event.target.value });
  }

  return (
    <>
      { loadingDone ? (
        images.files_left === 0 ? (
          <>
            <h1 className={ "pt-3" }>
              { "is_finished" in images ?
                "This project is already finished!" :
                "Congratulations! You scored this project!"
              }
            </h1>
            <Confetti
              width={ width }
              height={ height }
            />
          </>
        ) : (
          <>
            <Row md={ 8 } id={ `counter-${ images.files_left }` }>
              <Col className="mt-2">
                Images left: { images.files_left }
              </Col>
            </Row>

            <Row md={ 8 }>
              <Col className="mt-2">
                <img src={ getImathPath() } alt="Score-Image"/>
              </Col>
            </Row>
            <Row>
              <Col md={ 5 } className={ "pt-3" }>
                <Form.Group controlId="formComment">
                  <Form.Control type="text" className={ "input-form" }
                                placeholder="Comment (optional)"
                                value={ state.comment }
                                onChange={ changeCommentListener }/>
                </Form.Group>
              </Col>
            </Row>
            <Row className={ "py-4" }>

              <Col md={ 5 }>
                <ButtonGroup size="lg">
                  <Button variant={ state.active === actions[0] ? "info" : "primary" }
                          onClick={ () => dispatch({ type: actionTypes.SET_ACTIVE, payload: actions[0] }) }>Eyes
                    ({ state.eye || "?" })</Button>
                  <Button variant={ state.active === actions[1] ? "info" : "primary" }
                          onClick={ () => dispatch({ type: actionTypes.SET_ACTIVE, payload: actions[1] }) }>Nose
                    ({ state.nose || "?" })</Button>
                  <Button variant={ state.active === actions[2] ? "info" : "primary" }
                          onClick={ () => dispatch({ type: actionTypes.SET_ACTIVE, payload: actions[2] }) }>Cheeks
                    ({ state.cheek || "?" })</Button>
                  <Button variant={ state.active === actions[3] ? "info" : "primary" }
                          onClick={ () => dispatch({ type: actionTypes.SET_ACTIVE, payload: actions[3] }) }>Ears
                    ({ state.ear || "?" })</Button>
                  <Button variant={ state.active === actions[4] ? "info" : "primary" }
                          onClick={ () => dispatch({ type: actionTypes.SET_ACTIVE, payload: actions[4] }) }>Whiskers
                    ({ state.whiskers || "?" })</Button>
                </ButtonGroup>
              </Col>
            </Row>
            <Row md={ 7 }>
              <Col>
                <ScoreGroup callback={ selectCallback } action={ state.active }/>
              </Col>
            </Row>
            <Row>
              <Col>
                <Button size="lg" variant={ "success" } onClick={ () => confirmScore() }
                        disabled={ ( state.eye + state.nose + state.cheek + state.ear + state.whiskers ).length !== 5 }>Confirm</Button>
                <Button className={ "ms-2" } size="lg" variant={ "danger" } onClick={ () => markAsUseless() }>Mark as
                  Useless</Button>
              </Col>
            </Row>

          </>
        )
      ) : <Row><LoadingIcon/></Row> }
    </>

  );
};

export default ScoreView;
