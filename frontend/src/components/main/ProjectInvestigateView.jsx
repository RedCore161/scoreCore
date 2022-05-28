import React, { useEffect, useState } from "react";
import { Row } from "react-bootstrap";
import { useParams } from "react-router";
import BoxContainer from "../ui/BoxContainer";
import LoadingIcon from "../ui/LoadingIcon";
import axiosConfig from "../../axiosConfig";


const ProjectInvestigateView = () => {

  const { id } = useParams();

  const [data, setData] = useState({});

  useEffect(() => {
    investigateProject()
  }, []);

  async function investigateProject() {
    await axiosConfig.holder.get(`/api/project/${ id }/investigate/`, {
      "project": id
    }).then((response) => {
      if (response.data) {
        if (response.data.success) {
          setData(response.data);
        }
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
    data ? (
      <>
        <BoxContainer title={`Debug '${data.project}'`}>
          <Row>

          </Row>
        </BoxContainer>
      </>
    ) : ( <Row><LoadingIcon/></Row> )
  );
};

export default ProjectInvestigateView;
