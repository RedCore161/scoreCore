import React, { useLayoutEffect, useState } from "react";

import BoxContainer from "../ui/BoxContainer";
import { Row } from "react-bootstrap";
import ProjectCardView from "../ui/ProjectCardView";
import { fetchProjects } from "../../helper";

const IndexView = () => {

  const [data, setData] = useState([]);

  useLayoutEffect(() => {
    fetchProjects().then((projects) => {
      setData(projects)
    })
  }, []);

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

export default IndexView;
