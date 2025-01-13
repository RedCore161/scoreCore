import React, { useContext, useEffect, useLayoutEffect, useState } from "react";
import { Button, Col, Row } from "react-bootstrap";
import LoadingIcon from "../ui/LoadingIcon";
import BoxContainer from "../ui/BoxContainer";
import ProjectCardView from "../ui/ProjectCardView";
import { fetchProjects, updateOrAppend } from "../../helper";
import { CoreModalContext } from "../modal/coreModalContext";
import CreateProjectModal from "../modal/CreateProjectModal";
import UploadFolderModal from "../modal/UploadFolderModal";
import UploadFileModal from "../modal/UploadFileModal";
import { useAuth } from "../../../hooks/CoreAuthProvider";
import { useSnackbar } from "notistack";

const IndexView = () => {

  const [data, setData] = useState([]);
  const [modalState, setModalState] = useContext(CoreModalContext);
  const { enqueueSnackbar } = useSnackbar();

  const auth = useAuth();

  useEffect(() => {
    fetchProjects(auth, setData)
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
        <UploadFileModal callBackData={ callBackUpload } />

        <BoxContainer title="Available Projects">
          { auth?.user?.is_superuser && (
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
