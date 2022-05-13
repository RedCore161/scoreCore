import React, { useLayoutEffect, useReducer, useState } from "react";
import { useParams } from "react-router";

import { defaultStateScore, reducerScore } from "../reducer/reducerScore";
import { Button, ButtonGroup, Col, Row } from "react-bootstrap";
import useWindowSize from 'react-use/lib/useWindowSize';
import Confetti from 'react-confetti';

import * as actionTypes from "../reducer/reducerTypes";
import ScoreGroup from "../ui/ScoreGroup";
import { showErrorBar, showSuccessBar } from "../ui/Snackbar";
import { useSnackbar } from "notistack";
import axiosConfig from "../../axiosConfig";

const ScoreView = () => {

  const { id } = useParams();
  const [images, setImages] = useState([]);
  const [loadingDone, setLoadingDone] = useState(false);
  const [updateUi, setUpdateUi] = useState(false);
  const [state, dispatch] = useReducer(reducerScore, defaultStateScore);
  const { enqueueSnackbar } = useSnackbar();
  const { width, height } = useWindowSize();

  const actions = ["eye", "nose", "cheek", "ear", "whiskas"];

  async function fetchData() {
    const result = await axiosConfig.holder.get(`/api/project/${ id }/images`);
    setImages(result.data);
    setLoadingDone(true);
    console.log("Found Images:", result.data);
  }

  useLayoutEffect(() => {
    console.log("fetchData");
    fetchData();

  }, []);


  const selectCallback = (action, value) => {
    dispatch({ type: actionTypes.SET_SCORE, payload: { "action": action, "value": value } });
  };

  async function confirmScore() {
    let image = images.shift();
    await axiosConfig.holder.post(`/api/imagescore/${ image.id }/confirm/`, {
      'eye': state.eye,
      'nose': state.nose,
      'cheek': state.cheek,
      'ear': state.ear,
      'whiskas': state.whiskas,
    }).then((response) => {
      if (response.data) {
        if (response.data.success) {
          showSuccessBar(enqueueSnackbar, "Scoring confirmed!");
          setImages(images);
          dispatch({ type: actionTypes.SET_RESET });
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

  function skipImage() {
    images.shift();
    setImages(images);
    dispatch({ type: actionTypes.SET_RESET });
    setUpdateUi(!updateUi)
  }

  async function markAsUseless() {
    let image = images.shift();
    await axiosConfig.holder.post(`/api/imagescore/${ image.id }/useless/`, {
      "project": id
    }).then((response) => {
        if (response.data) {
          if (response.data.success) {
            showSuccessBar(enqueueSnackbar, "Image marked as Useless!");
            setImages(images);
            setUpdateUi(!updateUi)
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
    return [process.env.REACT_APP_BACKEND_URL, "media", images[0].rel_path, images[0].filename].join("/")
  }

  return (
    <>
      { loadingDone && (
        images.length === 0 ? (
            <>
              <h1 className={ "pt-3" }>Congratulations! You scored everything in this project!</h1>
              <Confetti
                width={ width }
                height={ height }
              />
            </> ) :
          (
            <>
              <Row md={ 8 } id={`counter-${images.length}`}>
                <Col className="mt-2">
                  Images left: { images.length }
                </Col>
              </Row>

              <Row md={ 8 }>
                <Col className="mt-2">
                  <img src={ getImathPath()} alt="Score-Image" />
                </Col>
              </Row>

              <Row className={ "py-4" }>

                <Col md={ 5 }>
                  <ButtonGroup size="lg">
                    <Button variant={ state.active === actions[0] ? "info" : "primary" }
                            onClick={ () => dispatch({ type: actionTypes.SET_ACTIVE, payload: actions[0] }) }>Eye
                      ({ state.eye || "?" })</Button>
                    <Button variant={ state.active === actions[1] ? "info" : "primary" }
                            onClick={ () => dispatch({ type: actionTypes.SET_ACTIVE, payload: actions[1] }) }>Nose
                      ({ state.nose || "?" })</Button>
                    <Button variant={ state.active === actions[2] ? "info" : "primary" }
                            onClick={ () => dispatch({ type: actionTypes.SET_ACTIVE, payload: actions[2] }) }>Cheek
                      ({ state.cheek || "?" })</Button>
                    <Button variant={ state.active === actions[3] ? "info" : "primary" }
                            onClick={ () => dispatch({ type: actionTypes.SET_ACTIVE, payload: actions[3] }) }>Ear
                      ({ state.ear || "?" })</Button>
                    <Button variant={ state.active === actions[4] ? "info" : "primary" }
                            onClick={ () => dispatch({ type: actionTypes.SET_ACTIVE, payload: actions[4] }) }>Whiskas
                      ({ state.whiskas || "?" })</Button>
                  </ButtonGroup>
                </Col>
                <Col>
                  <Button size="lg" variant={ "success" } onClick={ () => confirmScore() }
                          disabled={ ( state.eye + state.nose + state.cheek + state.ear + state.whiskas ).length !== 5 }>Confirm</Button>
                  <Button className={"ms-2"} size="lg" variant={ "primary" } onClick={ () => skipImage() }>Skip</Button>
                  <Button className={"ms-2"} size="lg" variant={ "danger" } onClick={ () => markAsUseless() }>Mark as Useless</Button>
                </Col>
              </Row>
              <Row md={ 7 }>
                <Col>
                  <ScoreGroup callback={ selectCallback } action={ state.active }/>
                </Col>

              </Row>

            </>
          )
      ) }
    </>

  );
};

export default ScoreView;
