import React, { useLayoutEffect, useState } from "react";

import BoxContainer from "../ui/BoxContainer";
import { Row } from "react-bootstrap";
import ProjectCardView from "../ui/ProjectCardView";
import axiosConfig from "../../axiosConfig";

const IndexView = () => {

  const [data, setData] = useState([]);

  useLayoutEffect(() => {
    axiosConfig.refreshData()
    fetchProjects();
  }, []);

  async function fetchProjects() {
    const result = await axiosConfig.holder.get("/api/project/list/");
    setData(result.data);
    console.log("Found Projects:", result.data);
  }

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
