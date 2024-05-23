import React, { useEffect, useLayoutEffect, useReducer, useState } from "react";
import { defaultStateScore, reducerScore } from "../reducer/reducerScore";
import { Form, Button, ButtonGroup, Col, Row } from "react-bootstrap";
import useWindowSize from "react-use/lib/useWindowSize";
import Confetti from "react-confetti";
import { showErrorBar, showSuccessBar } from "../ui/Snackbar";
import { useSnackbar } from "notistack";
import { useParams } from "react-router";
import { capitalizeFirstLetter, fetchImage, MULTISELECT_STYLE } from "../../helper";
import LoadingIcon from "../ui/LoadingIcon";
import ScoreGroup from "../ui/ScoreGroup";
import * as actionTypes from "../reducer/reducerTypes";
import axiosConfig from "../../axiosConfig";
import { useAuthHeader } from "react-auth-kit";
import { useSearchParams } from "react-router-dom";
import { Multiselect } from "multiselect-react-dropdown";
import Offcanvas from 'react-bootstrap/Offcanvas';
import "../ui/css/ScoreView.css";
import ScoreInfo from "../ui/ScoreInfo";

const ScoreView = () => {

  const { id } = useParams();
  const [images, setImages] = useState({ "files_left": 0 });
  const [loadingDone, setLoadingDone] = useState(false);
  const [uilock, setUILock] = useState(false);
  const [updateUi, setUpdateUi] = useState(false);
  const [selectedFeatures, setSelectedFeatures] = useState([]);
  const [state, dispatch] = useReducer(reducerScore, defaultStateScore);
  const [searchParams, setSearchParams] = useSearchParams();
  const { enqueueSnackbar } = useSnackbar();
  const { width, height } = useWindowSize();
  const [show, setShow] = useState(false);
  const authHeader = useAuthHeader();
  const handleClose = () => setShow(false);


  useLayoutEffect(() => {
    loadData(searchParams);
  }, []);

  const loadData = (params) => {
    console.log("fetchData", params);
    axiosConfig.updateToken(authHeader());
    fetchImage(id, params).then((data) => {
      setImages(data);
      setLoadingDone(true);
      setSelectedFeatures(data.features.map(ft => ft.id));
      dispatch({ type: actionTypes.SET_ACTIVE, payload: data.features[0].name });
    });
  };

  // useEffect(() => {
  //   console.log("selectedFeatures", selectedFeatures);
  // }, [selectedFeatures]);


  const selectCallback = (action, value) => {
    let _index = images.features.findIndex((ft) => ft.name === action);
    let _next = "";
    if (_index > -1 && _index < images.features.length - 1) {
      _next = images.features[_index + 1].name;
    }
    dispatch({ type: actionTypes.SET_SCORE, payload: { action: action, value: value, next: _next } });
  };

  async function confirmScore() {
    let image = images.image;
    if (uilock) {
      showErrorBar(enqueueSnackbar, "Another request isn't finished yet...");
      return;
    }
    setUILock(true);
    axiosConfig.updateToken(authHeader());
    await axiosConfig.holder.post(`/api/imagescore/${ image.id }/confirm/`, {
      ...state,
      "project": id,
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
    axiosConfig.updateToken(authHeader());
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

  function getImagePath() {
    return [process.env.REACT_APP_BACKEND_URL, "media", images.image.rel_path, images.image.filename].join("/");
  }

  function changeCommentListener(event) {
    dispatch({ type: actionTypes.SET_COMMENT, payload: event.target.value });
  }

  function _get_variant(name) {
    if (state.active === name) {
      return { variant: "info", clazz: "btnSelected" };
    }
    if (name in state) {
      return { variant: "success", clazz: "" };
    }
    return { variant: "primary", clazz: "" };
  }

  function get_state_score() {
    return 1; // TODO
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
            <Row md={ 8 } className="mt-2" id={ `counter-${ images.files_left }` }>
              <Col>
                <Form.Group>
                  <Form.Label>
                    Rate features
                  </Form.Label>
                  <Multiselect
                    displayValue="name"
                    groupBy="level"
                    onKeyPressFn={ function noRefCheck() {
                    } }
                    onRemove={ (selectedList) => setSelectedFeatures(selectedList.map(obj => obj.id)) }
                    onSelect={ (selectedList) => setSelectedFeatures(selectedList.map(obj => obj.id)) }
                    placeholder={ "Select Features" }
                    options={ images.features }
                    selectedValues={ images.features }
                    showCheckbox
                    style={ MULTISELECT_STYLE }
                  />
                </Form.Group>
              </Col>
              <Col md={ 4 }>
                Images left: { images.files_left }
              </Col>
            </Row>

            <Row md={ 8 }>
              <Col className="mt-2">
                <img src={ getImagePath() } alt="Score-Image"/>
              </Col>
            </Row>

            <Row>
              <Col md={ 5 } className={ "pt-3" }>
                <Form.Group controlId="formComment">
                  <Form.Control type="text" className={ "input-form" }
                                placeholder="Comment (optional)"
                                value={ state._comment }
                                onChange={ changeCommentListener }/>
                </Form.Group>
              </Col>
            </Row>

            <Row className={ "py-4" }>
              <Col md={ 8 }>
                <ButtonGroup size="lg">
                  { images.features.map((feature, index) => {
                    let style = _get_variant(feature.name);
                    return <Button variant={ style.variant }
                                   className={ style.clazz }
                                   disabled={ !selectedFeatures.includes(feature.id) }
                                   key={ `btn-grp-${ index }` }
                                   onClick={ () => dispatch({
                                     type: actionTypes.SET_ACTIVE,
                                     payload: feature.name
                                   }) }>
                      { capitalizeFirstLetter(feature.name) } ({ feature.name in state ? state[feature.name] : "?" })
                    </Button>;
                  }) }

                </ButtonGroup>
              </Col>
            </Row>

            <Row md={ 8 }>
              <Col>
                <ScoreGroup callback={ selectCallback } action={ state.active }/>
              </Col>
            </Row>

            <Row>
              <Col>
                <Button size="lg" variant={ "success" } onClick={ () => confirmScore() }
                        disabled={ get_state_score() === 0 }>
                  Confirm
                </Button>
                <Button className={ "ms-2" } size="lg" variant={ "danger" } onClick={ () => markAsUseless() }>
                  Mark as Useless
                </Button>
                <Button className={ "ms-2" } size="lg" variant={ "primary" } onClick={ () => setShow(true) }>
                  Show History
                </Button>
              </Col>
            </Row>
            <Offcanvas show={ show } onHide={ handleClose } placement={ "end" } name={ "Scoring History" }>
              <Offcanvas.Header closeButton>
                <Offcanvas.Title>Scoring History</Offcanvas.Title>
              </Offcanvas.Header>
              <Offcanvas.Body>
                { images.history && images.history.map(score => {
                  return <ScoreInfo score={ score }
                                    features={ images.features }
                                    key={ `sc-info-${ score.id }` }/>;
                }) }
              </Offcanvas.Body>
            </Offcanvas>
          </>
        )
      ) : <Row><LoadingIcon/></Row> }
    </>
  );
};

export default ScoreView;
