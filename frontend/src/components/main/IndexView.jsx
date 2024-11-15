import React, { useContext, useLayoutEffect, useState } from "react";
import { Button, Col, Row } from "react-bootstrap";
import LoadingIcon from "../ui/LoadingIcon";
import BoxContainer from "../ui/BoxContainer";
import ProjectCardView from "../ui/ProjectCardView";
import { fetchProjects, updateOrAppend } from "../../helper";
import useAuthHeader from 'react-auth-kit/hooks/useAuthHeader';
import axiosConfig from "../../axiosConfig";
import { CoreModalContext } from "../modal/coreModalContext";
import CreateProjectModal from "../modal/CreateProjectModal";
import UploadFolderModal from "../modal/UploadFolderModal";
import { useSnackbar } from "notistack";
import UploadFileModal from "../modal/UploadFileModal";
import useAuthUser from "react-auth-kit/hooks/useAuthUser";

const IndexView = () => {

  const [data, setData] = useState([]);
  const [modalState, setModalState] = useContext(CoreModalContext);
  const { enqueueSnackbar } = useSnackbar();

  const authHeader = useAuthHeader();
  const auth = useAuthUser();
  const isAuth = auth();

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
        <UploadFileModal enqueueSnackbar={ enqueueSnackbar } callBackData={ callBackUpload } />

        <BoxContainer title="Available Projects">
          { isAuth.is_superuser && (
            <Row className={"pb-3"}>
              <Col>
                <Button className={"me-2"} variant={"warning"} onClick={() => setModalState({ ...modalState, modalUploadFolder: true, title: "Upload folder" })}>1a. Upload Folder</Button>
                <Button className={"me-2"} variant={"warning"} onClick={() => setModalState({ ...modalState, modalUploadFiles: true, title: "Upload images/videos" })}>1b. Upload Images/Videos</Button>
                <Button className={"me-2"} variant={"warning"} onClick={() => setModalState({ ...modalState, modalProjectModal: true })}>2. Create New Project</Button>
                <Button className={"me-2"} variant={"primary"} href={`${process.env.REACT_APP_BACKEND_URL}/admin/auth/user/add/`} target={"_blank"}>Add User</Button>
              </Col>
            </Row>
          )}

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
