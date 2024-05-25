import React, { useContext, useLayoutEffect, useState } from "react";
import { Row } from "react-bootstrap";
import LoadingIcon from "../ui/LoadingIcon";
import BoxContainer from "../ui/BoxContainer";
import ProjectCardView from "../ui/ProjectCardView";
import { fetchProjects } from "../../helper";
import { useAuthHeader } from "react-auth-kit";
import axiosConfig from "../../axiosConfig";
import { CoreModalContext } from "../modal/coreModalContext";

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

  function createProject() {
    setModalState({ ...modalState, modalProjectModal: true, });
  }

  return (
    data ? (
      <BoxContainer title="Available Projects">
        <Row>
          { data.map((project) => {
            return <ProjectCardView key={ project.id }
                                    createProject={ createProject }
                                    { ...project } />;
          }) }
        </Row>
      </BoxContainer>
    ) : ( <Row><LoadingIcon/></Row> )
  );


};

export default IndexView;
