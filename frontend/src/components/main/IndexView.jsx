import React, { useContext, useLayoutEffect, useState } from "react";
import { Button, Col, Row } from "react-bootstrap";
import LoadingIcon from "../ui/LoadingIcon";
import BoxContainer from "../ui/BoxContainer";
import ProjectCardView from "../ui/ProjectCardView";
import { fetchProjects, updateOrAppend } from "../../helper";
import { useAuthHeader } from "react-auth-kit";
import axiosConfig from "../../axiosConfig";
import { CoreModalContext } from "../modal/coreModalContext";
import CreateProjectModal from "../modal/CreateProjectModal";
import UploadFolderModal from "../modal/UploadFolderModal";
import { useSnackbar } from "notistack";

const IndexView = () => {

  const [data, setData] = useState([]);
  const [modalState, setModalState] = useContext(CoreModalContext);
  const { enqueueSnackbar } = useSnackbar();

  const authHeader = useAuthHeader();

  useLayoutEffect(() => {
    axiosConfig.updateToken(authHeader());
    fetchProjects().then((projects) => {
      setData(projects);
    });
  }, []);

  const callBackData = (response) => {
    let elements = updateOrAppend(data, response)
    setData(elements)
  }

  const callBackUpload = () => {
    // TODO
  }

  return (
    data ? (
      <div>
        <CreateProjectModal callBackData={ callBackData } />
        <UploadFolderModal enqueueSnackbar={ enqueueSnackbar } callBackData={ callBackUpload } />

        <BoxContainer title="Available Projects">
          <Row className={"pb-3"}>
            <Col>
              <Button className={"me-2"} variant={"warning"} onClick={() => setModalState({ ...modalState, modalUploadFolder: true, title: "Upload images-folder" })}>1. Upload Images</Button>
              <Button className={"me-2"} variant={"warning"} onClick={() => setModalState({ ...modalState, modalProjectModal: true })}>2. Create New Project</Button>
              <Button className={"me-2"} variant={"primary"} href={`${process.env.REACT_APP_BACKEND_URL}/admin/auth/user/add/`} target={"_blank"}>Add User</Button>
            </Col>
          </Row>

          <Row>
            { data.map((project) => {
              return <ProjectCardView key={ project.id } { ...project } />
            })}
          </Row>

        </BoxContainer>
      </div>
    ) : ( <Row><LoadingIcon/></Row> )
  );
};
export default IndexView;
