import React, { useEffect, useState } from "react";
import { Col, Row } from "react-bootstrap";
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
        <BoxContainer title={`Debug '${"project" in data && data.project.name}'`}>

          <Row>
            <Col md={2}>ImageFiles</Col>
            <Col>{ data.imageFilesCount }</Col>
          </Row>

          <Row className={"py-3"}>
            <Col md={2}>Scores foreach ImageFiles</Col>
            <Col>{ "scoreCount" in data && Object.keys(data.scoreCount).map(function(key, index) {
              let obj = data.scoreCount[key]
              return <div key={index}>[{index}] {obj.filename} - { obj.scores }<br/></div>
            })}
            </Col>
          </Row>

          <Row className={"py-3"}>
            <Col md={2}>Scores per User</Col>
            <Col>{ "scoresPerUser" in data && Object.keys(data.scoresPerUser).map(function(key, index) {
              return <div key={index}>{key}: {data.scoresPerUser[key]}<br/></div>
            })}
            </Col>
          </Row>

        </BoxContainer>
      </>
    ) : ( <Row><LoadingIcon/></Row> )
  );
};

export default ProjectInvestigateView;
