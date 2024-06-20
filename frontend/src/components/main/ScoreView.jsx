import React, { useLayoutEffect, useReducer, useState } from "react";
import { defaultStateScore, reducerScore } from "../reducer/reducerScore";
import { Form, Button, ButtonGroup, Col, Row } from "react-bootstrap";
import useWindowSize from "react-use/lib/useWindowSize";
import Confetti from "react-confetti";
import { showErrorBar, showSuccessBar } from "../ui/Snackbar";
import { useSnackbar } from "notistack";
import { useParams } from "react-router";
import {
  capitalizeFirstLetter,
  fetchImage
} from "../../helper";
import LoadingIcon from "../ui/LoadingIcon";
import ScoreGroup from "../ui/ScoreGroup";
import ScorePanel from "../ui/ScorePanel";
import * as actionTypes from "../reducer/reducerTypes";
import axiosConfig from "../../axiosConfig";
import { useAuthHeader } from "react-auth-kit";
import { useNavigate, useSearchParams } from "react-router-dom";
import "../ui/css/ScoreView.css";


const ScoreView = () => {

  const { id } = useParams();
  const [images, setImages] = useState({ "files_left": 0 });
  const [loadingDone, setLoadingDone] = useState(false);
  const [uilock, setUILock] = useState(false);
  const [updateUi, setUpdateUi] = useState(false);
  const [state, dispatch] = useReducer(reducerScore, defaultStateScore);
  const [searchParams, setSearchParams] = useSearchParams();
  const { enqueueSnackbar } = useSnackbar();
  const { width, height } = useWindowSize();
  const authHeader = useAuthHeader();
  const navigate = useNavigate();

  useLayoutEffect(() => {
    dispatch({ type: actionTypes.SET_RESET });
    loadData(searchParams);
  }, [searchParams]);

  const onSelectImage = (params) => {
    setSearchParams(params);
  };

  const resetPage = () => {
    navigate(`/project/${ id }/score/`);
    setSearchParams({ reload: Date.now() });
  };

  function findSelectNextActive(data, init = undefined) {
    let keys = init ? Object.keys(init) : Object.keys(state).filter(s => s[0] !== "_");
    let next = data?.features.filter(ft => !keys.some(s => s === ft.name));

    if (next && next.length > 0) {
      dispatch({ type: actionTypes.SET_ACTIVE, payload: next[0].name });
    }
  }

  const loadData = (params) => {
    console.log("loadData", params);
    axiosConfig.updateToken(authHeader());
    fetchImage(id, params).then((data) => {
      setImages(data);
      setLoadingDone(true);
      let init = data?.score?.data;
      if (data?.score?.comment) {
        dispatch({ type: actionTypes.SET_COMMENT, payload: data.score.comment });
      }
      if (init) {
        Object.keys(init).forEach(key => {
          if (init[key] === null) {
            delete init[key];
          }
        });
        dispatch({ type: actionTypes.SET_INIT, payload: init });
        findSelectNextActive(data, init);
      } else {
        data?.features && dispatch({ type: actionTypes.SET_ACTIVE, payload: data.features[0].name });
      }
    });
  };

  const selectCallback = (action, value) => {
    if (action.length === 0) {
      return;
    }
    dispatch({ type: actionTypes.SET_SCORE, payload: { action: action, value: value } });
    let obj = {};
    obj[action] = value;
    findSelectNextActive(images, { ...state, ...obj });
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
          findSelectNextActive(response.data);
          resetPage();

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
    if (images?.image) {
      return [process.env.REACT_APP_BACKEND_URL, images?.image.path, images?.image.filename].join("/");
    }
    return "";
  }

  function changeCommentListener(event) {
    dispatch({ type: actionTypes.SET_COMMENT, payload: event.target.value });
  }

  function _get_variant(name) {
    if (state._active === name) {
      return { variant: "info", clazz: "btnSelected" };
    }
    if (name in state) {
      return { variant: "success", clazz: "" };
    }
    return { variant: "primary", clazz: "" };
  }

  function get_state_score() {
    return Object.keys(state).filter(e => e[0] !== "_").length;
  }

  function get_feature_option_count() {
    const feature = images?.features?.find(i => i.name === state._active);
    return feature?.option_count ? feature.option_count : 3;
  }

  return (
    <>
      { loadingDone ? (
        images?.is_finished || images.score_finished >= images.score_desired ? (
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
          ) :
          <Row>
            { images?.image ? (
              <Col md={ 8 }>
                <Row className="mt-4">
                  <Col>
                    <img src={ getImagePath() } alt={ `Missing Score-Image ${images?.image.filename}` } />
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

                <Row>
                  <Col>
                    <ScoreGroup callback={ selectCallback } options={ get_feature_option_count() }
                                action={ state._active }/>
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
                    <Button className={ "ms-2" } size="lg" variant={ "outline-primary" } onClick={ () => resetPage() }>
                      Load {images.count === 0 ? "latest" : "random"} Image
                    </Button>
                  </Col>
                </Row>
              </Col>
            ) : <Row><LoadingIcon/></Row> }

            <Col className={ "mt-2" }>
              {/* History-Side-Panel */ }
              <ScorePanel images={ images } id={ id } callback={ onSelectImage }/>
            </Col>
          </Row>
      ) : <Row><LoadingIcon/></Row> }
    </>
  );
};
export default ScoreView;
