import React, { useLayoutEffect, useState } from "react";

import BoxContainer from "../ui/BoxContainer";
import { Button, Row } from "react-bootstrap";
import ProjectCardView from "../ui/ProjectCardView";
import { fetchProjects } from "../../helper";
import LoadingIcon from "../ui/LoadingIcon";

const IndexView = () => {

  const [data, setData] = useState([]);

  useLayoutEffect(() => {
    fetchProjects().then((projects) => {
      setData(projects);
    });
  }, []);

  return (
    data ? (
      <BoxContainer title="Available Projects">
        <Row>
          { data.map((project) => {
            return <ProjectCardView key={ project.id }
                                    { ...project } />;
          }) }
        </Row>
      </BoxContainer>
    ) : ( <Row><LoadingIcon/></Row> )
  );


};

export default IndexView;
