import React, { useEffect, useState } from "react";
import { Col, Row, Collapse, Button } from "react-bootstrap";
import { Link } from "@material-ui/core";

import { useParams } from "react-router";
import BoxContainer from "../ui/BoxContainer";
import LoadingIcon from "../ui/LoadingIcon";
import axiosConfig from "../../axiosConfig";
import Tooltip from "@material-ui/core/Tooltip";


const ScoreFileLink = ({id, filename, path}) => {
  function getImagePath() {
    return [process.env.REACT_APP_BACKEND_URL, "media", path, filename].join("/");
  }

  return (
    <div key={ `file-${id}` }>
      <Link color={"initial"} target={"_blank"} href={getImagePath()}>{ filename }</Link><br/>
    </div>
  )
}

const ProjectInvestigateView = () => {

  const { id } = useParams();

  const [data, setData] = useState({});
  const [collapsed, setCollapsed] = useState({ });

  useEffect(() => {
    investigateProject();
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

  function changeCollapse(value) {
    let obj = {}
    if (!value in collapsed) {
      obj[value] = true
    } else {
      obj[value] = !collapsed[value]
    }
    setCollapsed({...collapsed, ...obj })
  }

  return (
    Object.keys(data).length > 0 ? (
      <>
        <BoxContainer title={ `Investigate '${ "project" in data && data.project.name }'` }>
          <Row>
            <Col md={ 2 }>ImageFiles</Col>
            <Col>{ data.imageFilesCount }</Col>
          </Row>

          <Row className={ "py-3" }>
            <Col md={ 2 }>Scores foreach ImageFiles</Col>
            <Col>{ "scoreCount" in data && Object.keys(data.scoreCount).map(function (count, index) {
              let objects = data.scoreCount[count];
              let _elements = objects.map(obj => <ScoreFileLink {...obj} />);
              return <div key={ `block-${index}` }>
                      <div style={ { fontWeight: "bold" } }>
                        <Tooltip title={"Click to see Files"} placement={"right"}>
                          <Button className={"mt-4 mb-1"} ak onClick={() => changeCollapse(count)}>
                            Images with { count === "1" ? "1 score" : `${count} scores` } ({objects.length})
                          </Button>
                        </Tooltip>
                        <br/>
                      </div>
                        <Collapse in={ count in collapsed && collapsed[count] }>
                          <div>{ _elements }</div>
                        </Collapse>
                     </div>
            })}
            </Col>
          </Row>

          <Row className={ "py-3" }>
            <Col md={ 2 }>Scores per User</Col>
            <Col>{ "scoresPerUser" in data && Object.keys(data.scoresPerUser).map(function (key, index) {
              return <div key={ index }>{ key }: { data.scoresPerUser[key] }<br/></div>;
            }) }
            </Col>
          </Row>

        </BoxContainer>
      </>
    ) : ( <Row><LoadingIcon/></Row> )
  );
};

export default ProjectInvestigateView;
