import React, { useEffect, useLayoutEffect, useState } from "react";

import BoxContainer from "../ui/BoxContainer";
import { Button, Col, Row } from "react-bootstrap";
import axiosConfig from "../../axiosConfig";
import { fetchProjects, SelectListened } from "../../helper";
import { showErrorBar, showSuccessBar } from "../ui/Snackbar";
import { useSnackbar } from "notistack";

import { useAuth } from "../../../hooks/CoreAuthProvider";

const ProjectEvaluateView = () => {

  const [evaluations, setEvaluations] = useState([]);
  const [data, setData] = useState([]);
  const [selectedProject, setSelectedProject] = useState({});

  const { enqueueSnackbar } = useSnackbar();
  const auth = useAuth();

  useLayoutEffect(() => {
    fetchProjects(auth, setData).then((projects) => {
      setData(projects);
    });
  }, []);

  useEffect(() => {
    if (data) {
      setSelectedProject(data[0]);
      setEvaluations(data[0].evaluations.files);
    }
  }, [data]);

  function onSelectProject(projectName) {
    const selected = data.filter((project) => project.name === projectName)[0];
    setSelectedProject(selected);
    setEvaluations(selected.evaluations.files);
  }

  async function deleteExports() {
    await _export("clear", "Deleted all files", "Couldn't delete files");
  }

  async function exportAsExcel() {
    await _export("xlsx", "Evaluation File was created!", "Couldn't create evaluation File");
  }

  async function _export(url_sub, msg, err) {
    await axiosConfig.perform_post(auth, `/api/project/${ selectedProject.id }/export/${ url_sub }/`, {
        "project": selectedProject.id
      },
      (response) => {
        if (response.data) {
          if (response.data.success) {
            showSuccessBar(enqueueSnackbar, msg);
            console.log(response.data.files);
            setEvaluations(response.data.files);
          }
        } else {
          showErrorBar(enqueueSnackbar, err);
        }
      }, (error) => {
        if (error.response) {
          console.error(error.response.data);
        } else {
          console.error(error);
        }
      });
  }

  async function evaluateProject() {
    console.log(selectedProject);
    await axiosConfig.perform_post(auth, `/api/project/${ selectedProject.id }/evaluate/`, {
        "project": selectedProject.id
      },
      (response) => {
        if (response.data) {
          if (response.data.success) {
            showSuccessBar(enqueueSnackbar, "Evaluation JSON was created!");
            console.log(response.data.files);
            setEvaluations(response.data.files);
          }
        } else {
          showErrorBar(enqueueSnackbar, "Couldn't create evaluation JSON");
        }
      }, (error) => {
        if (error.response) {
          console.error(error.response.data);
        } else {
          console.error(error);
        }
      });
  }

  return (
    data && (
      <>
        <BoxContainer title="Evaluate Projects">
          <Row>
            <Col md={ 2 }>Select Project: </Col>
            <Col md={ 3 }>
              <SelectListened options={ data.map((project) => project.name) }
                              onChange={ (e) => onSelectProject(e.target.value) }/>
            </Col>
          </Row>

          <Row>
            {/*<Col md={3} >*/ }
            {/*  <Button onClick={ () => evaluateProject() }>Evaluate</Button>*/ }
            {/*</Col>*/ }
            <Col>
              <Button onClick={ () => exportAsExcel() }>Export as Xlsx</Button>
              <Button className={ "ms-3" } variant={ "danger" } onClick={ () => deleteExports() }>Delete existing
                files</Button>
            </Col>
          </Row>
        </BoxContainer>

        { evaluations.length > 0 && (
          <BoxContainer title="Evaluation Files">
            <Row>
              { evaluations.map((evaluation) => (
                <Col key={ evaluation } md={ 3 } className={ "mb-3" }>
                  <Button className={ "px-5" }
                          href={ `${ process.env.REACT_APP_BACKEND_URL }/media/evaluations/${ selectedProject.id }/${ evaluation }` }
                          target={ "_blank" }>{ evaluation }</Button>
                </Col>
              )) }
            </Row>
          </BoxContainer>
        ) }
      </>
    )
  );
};
export default ProjectEvaluateView;
