import React, { useContext, useLayoutEffect, useState } from "react";
import { Button, Col, Row } from "react-bootstrap";
import LoadingIcon from "../ui/LoadingIcon";
import BoxContainer from "../ui/BoxContainer";
import ProjectCardView from "../ui/ProjectCardView";
import { fetchProjects } from "../../helper";
import { useAuthHeader } from "react-auth-kit";
import axiosConfig from "../../axiosConfig";
import { CoreModalContext } from "../modal/coreModalContext";
import CreateProjectModal from "../modal/CreateProjectModal";

const IndexView = () => {

  const [data, setData] = useState([]);
  const [modalState, setModalState] = useContext(CoreModalContext);

  const authHeader = useAuthHeader();

  useLayoutEffect(() => {
    axiosConfig.updateToken(authHeader());
    fetchProjects().then((projects) => {
      setData(projects);
    });
  }, []);

  const callBackData = () => {
    // TODO
  }

  return (
    data ? (
      <div>
        <CreateProjectModal callBackData={ callBackData } />
        <BoxContainer title="Available Projects">
          <Row className={"pb-3"}>
            <Col>
              <Button variant={"warning"} onClick={() => setModalState({ ...modalState, modalProjectModal: true })}>Create New Project</Button>
            </Col>
          </Row>
          <Row>
            { data.map((project) => {
              return <ProjectCardView key={ project.id }
                                      { ...project } />;
            }) }
          </Row>
        </BoxContainer>
      </div>
    ) : ( <Row><LoadingIcon/></Row> )
  );


};

export default IndexView;
