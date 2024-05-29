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
  columnScores,
  conditionalScoreRowStyles,
  fetchImage,
  MULTISELECT_STYLE
} from "../../helper";
import LoadingIcon from "../ui/LoadingIcon";
import ScoreGroup from "../ui/ScoreGroup";
import ScorePanel from "../ui/ScorePanel";
import * as actionTypes from "../reducer/reducerTypes";
import axiosConfig from "../../axiosConfig";
import { useAuthHeader } from "react-auth-kit";
import { useSearchParams } from "react-router-dom";
import { Multiselect } from "multiselect-react-dropdown";

import "../ui/css/ScoreView.css";
import { FormControlLabel, Switch } from "@mui/material";
import DataTable from "react-data-table-component";
import Offcanvas from "react-bootstrap/Offcanvas";

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
      setSelectedFeatures(data?.features.map(ft => ft.id));
      let init = data?.score?.data
      if (init) {
        Object.keys(init).forEach(key => {
          if (init[key] === null) {
            delete init[key];
          }
        });
        dispatch({ type: actionTypes.SET_INIT, payload: init});
      }
      dispatch({ type: actionTypes.SET_ACTIVE, payload: data?.features[0].name });
    });
  };

  const selectCallback = (action, value) => {
    if (action.length === 0) {
      return
    }
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
          dispatch({ type: actionTypes.SET_ACTIVE, payload: images.features[0].name });
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
    return [process.env.REACT_APP_BACKEND_URL, images.image.path, images.image.filename].join("/");
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
    return Object.keys(state).filter(e => e[0] !== "_").length
  }

  function get_feature_option_count() {
    const feature = images?.features?.find(i => i.name === state._active)
    return feature?.option_count ? feature.option_count : 3
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
          <Row>
            <Col md={ 8 }>
              <Row className={ "mt-2" } id={ `counter-${ images.files_left }` }>
                <Col>
                  <Form.Group>
                    <Form.Label>
                      Active rating features
                    </Form.Label>
                    <Multiselect
                      displayValue="name"
                      groupBy="level"
                      onKeyPressFn={ function noRefCheck() {} }
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

              <Row className={ "mt-2" }>
                <Col>
                  <Button size="lg" variant={ "primary" } onClick={ () => setShow(true) }>
                    Show History
                  </Button>
                </Col>
              </Row>

              <Row>
                <Col className="mt-2">
                  <img src={ getImagePath() } alt="Score-Image" />
                </Col>
              </Row>

              <Row>
                <Col md={ 5 } className={ "pt-3" }>
                  <Form.Group controlId="formComment">
                    <Form.Control type="text" className={ "input-form" }
                                  placeholder="Comment (optional)"
                                  value={ state._comment }
                                  onChange={ changeCommentListener } />
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

              <Row>
                <Col>
                  <ScoreGroup callback={ selectCallback }
                              options={ get_feature_option_count() }
                              action={ state._active } />
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
                </Col>
              </Row>

              <Row className={"mt-2"}>
                <Col>
                  <Button size="lg" variant={ "primary" } onClick={ () => setShow(true) }>
                    Show History
                  </Button>
                </Col>
              </Row>

              {/* History-Side-Panel */}
              <ScorePanel images={ images } show={show} handleClose={handleClose} />

            </Col>
            <Col className={"mt-2"}>
              {/*<Form.Group controlId="formHide" className={"pb-3"}>*/}
              {/*  <FormControlLabel*/}
              {/*    control={ <Switch checked={ hideCompleted }*/}
              {/*                      onChange={ (e) => setHideCompleted(e.target.checked) }*/}
              {/*                      name="hideCompleted" /> }*/}
              {/*    label="Hide completed?"*/}
              {/*  />*/}
              {/*</Form.Group>*/}

              <DataTable
                columns={ columnScores }
                conditionalRowStyles={ conditionalScoreRowStyles }
                data={ images.history }
                onRowClicked={(row) => window.location.replace(`/project/${id}/score/?file=${row.file}`)}
                highlightOnHover
                defaultSortFieldId={ 2 }
                defaultSortAsc={ false }
                fixedHeader={ true }
                allowOverflow={ false }
                theme="dark"
              />
            </Col>

          </Row>
        )
      ) : <Row><LoadingIcon/></Row> }
    </>
  );
};
export default ScoreView;
