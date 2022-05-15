import React, { useLayoutEffect, useState } from "react";

import BoxContainer from "../ui/BoxContainer";
import { Row } from "react-bootstrap";
import ProjectCardView from "../ui/ProjectCardView";
import axiosConfig from "../../axiosConfig";

const BackupView = () => {

  const [data, setData] = useState([]);

  // useLayoutEffect(() => {
  //   axiosConfig.refreshData()
  //   fetchProjects();
  // }, []);



  return (
    <BoxContainer title="Available Projects">
      <Row>
        { data && data.map((project) => {
          return <ProjectCardView key={project.id} { ...project } />;
        }) }
      </Row>
    </BoxContainer>
  );
};

export default BackupView;
