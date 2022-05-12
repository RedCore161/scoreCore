import React, { useEffect, useState } from "react";
import axiosConfig from "../../axiosConfig";
import BoxContainer from "../ui/BoxContainer";
import { Row } from "react-bootstrap";
import ProjectCardView from "../ui/ProjectCardView";

const IndexView = () => {

    const [data, setData] = useState([]);

    useEffect(() => {
        console.log("useEffect");

        fetchProjects();

    }, []);

    async function fetchProjects() {
        const result = await axiosConfig.get("/api/project/list/");
        setData(result.data);
        console.log("Found Projects:", result.data);
    }

    return (
      <BoxContainer title="Available Projects">
          <Row>
              { data && data.map((project) => {
                return <ProjectCardView {...project} />
              }) }
          </Row>
      </BoxContainer>
    );
};

export default IndexView;
