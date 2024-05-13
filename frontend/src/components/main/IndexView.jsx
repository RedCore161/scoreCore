import React, { useLayoutEffect, useState } from "react";
import { Row } from "react-bootstrap";
import LoadingIcon from "../ui/LoadingIcon";
import BoxContainer from "../ui/BoxContainer";
import ProjectCardView from "../ui/ProjectCardView";
import { fetchProjects } from "../../helper";
import { useAuthHeader } from "react-auth-kit";
import axiosConfig from "../../axiosConfig";

const IndexView = () => {

  const [data, setData] = useState([]);
  const authHeader = useAuthHeader();

  useLayoutEffect(() => {
    axiosConfig.updateToken(authHeader());
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
