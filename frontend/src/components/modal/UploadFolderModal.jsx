import React, { useContext, useEffect, useMemo, useState } from "react";
import { Button, Col, Form, Modal, Row } from "react-bootstrap";
import { CoreModalContext } from "./coreModalContext";
import axiosConfig from "../../axiosConfig";
import { useDropzone } from "react-dropzone";
import { showErrorBar, showSuccessBar } from "../ui/Snackbar";
import { getAcceptesTypes } from "../datatables/configs";
import { fetchFolders } from "../../helper";

const UploadFolderModal = ({enqueueSnackbar, accept = "image", callBackData = () => {} }) => {

  const [show, setShow] = useContext(CoreModalContext);
  const [dirName, setDirName] = useState(undefined);
  const [folders, setFolders] = useState([]);

  const _types = getAcceptesTypes(accept);
  const config = { webkitdirectory: true, directory: true }

  const dropzoneOptions = {
    accept: _types,
    maxSize: 1024 * 1024 * 5, // 5 MB
    onDrop: (acceptedFiles) => {
      console.log("Files dropped:", acceptedFiles);
    },
    onDropRejected: (fileRejections) => {
      console.log("Rejected files:", fileRejections);
    },
    // Other options as needed
  };

  let acceptedFiles, getRootProps, getInputProps, isFocused, isDragAccept, isDragReject;
  ( { acceptedFiles, getRootProps, getInputProps, isFocused, isDragAccept, isDragReject } = useDropzone(dropzoneOptions) );

  const baseStyle = {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    padding: "20px",
    borderWidth: 2,
    borderRadius: 2,
    borderColor: "#eeeeee",
    borderStyle: "dashed",
    backgroundColor: "#fafafa",
    color: "#bdbdbd",
    outline: "none",
    transition: "border .24s ease-in-out"
  };

  const focusedStyle = {
    borderColor: "#2196f3"
  };

  const acceptStyle = {
    borderColor: "#00e676"
  };

  const rejectStyle = {
    borderColor: "#ff1744"
  };

  const style = useMemo(() => ( {
    ...baseStyle,
    ...( isFocused ? focusedStyle : {} ),
    ...( isDragAccept ? acceptStyle : {} ),
    ...( isDragReject ? rejectStyle : {} )
  } ), [
    isFocused,
    isDragAccept,
    isDragReject
  ]);

  useEffect(() => {
    if (show.modalUploadFolder && folders.length === 0) {
      fetchFolders(setFolders);
    }
  }, []);

  useEffect(() => {
    if (acceptedFiles.length) {
      uploadFile();
    }
  }, [acceptedFiles]);

  useEffect(() => {
    if (show.modalUploadFolder) {
    }
  }, [show]);

  async function uploadFile() {
    let formData = new FormData();
    dirName && formData.append("projectName", dirName);
    acceptedFiles.map((file, index) => {
      formData.append(`files${ index }`, file, file.name);
    });

    await axiosConfig.holder.post("/api/project/upload/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      }
    }).then((response) => {
      if (response.data.success) {
        showSuccessBar(enqueueSnackbar, "Successfully uploaded File(s)");
        callBackData(response.data);
        handleClose();
      } else {
        showErrorBar(enqueueSnackbar, "Failed uploading!");
      }
    }, (error) => {
      if (error.response) {
        console.error(error.response.data);
      } else {
        console.error(error);
      }
    });
  }

  const handleClose = () => {
    setShow((show) => ( { ...show, modalUploadFolder: false } ));
  };


  return (
    <Form>
      <Modal show={ show.modalUploadFolder } onHide={ handleClose } dialogClassName={ "wide-modal" }>
        <Modal.Header>
          <Modal.Title>{ show.title } to '&lt;upload-dir&gt;/projects/{ dirName }'</Modal.Title>
        </Modal.Header>
        <Modal.Body>

          <Row className={ "pb-3" }>
            <Col>
              <Form.Control type="text" placeholder={ "Directory-name..." }
                            value={ dirName }
                            onChange={ (e) => setDirName(e.target.value) }/>
            </Col>
          </Row>
          <Row>
            <Col>
              { dirName?.length > 0 && (
                folders?.data?.map(e => e.name).includes(dirName) ? (
                  <div className={ "modalErrors" }>Folder already exists</div>
                ) : (
                  <Form.Group controlId="formValue">
                    <div { ...getRootProps({ style }) }>
                      <input { ...getInputProps() } {...config} multiple/>
                      <p>Drag 'n' drop some files here, or click to select files</p>
                    </div>
                  </Form.Group>
                ) ) }
            </Col>
          </Row>
        </Modal.Body>

        <Modal.Footer>
          <Button variant="secondary" onClick={ handleClose }>Close</Button>
        </Modal.Footer>
      </Modal>
    </Form>
  );
};
export default UploadFolderModal;
