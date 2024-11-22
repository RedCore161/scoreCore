import React, { useContext, useEffect, useMemo, useReducer, useState } from "react";
import { Button, Col, Form, Modal, Row } from "react-bootstrap";
import { CoreModalContext } from "./coreModalContext";
import axiosConfig from "../../axiosConfig";
import { useDropzone } from "react-dropzone";
import { showErrorBar, showSuccessBar } from "../ui/Snackbar";
import { getAcceptesTypes } from "../datatables/configs";
import { fetchFolders } from "../../helper";
import LoadingIcon from "../ui/LoadingIcon";
import { defaultStateUpload, reducerUpload } from "../reducer/reducerUpload";
import * as actionTypes from "../reducer/reducerTypes";

const UploadFolderModal = ({
                             enqueueSnackbar, accept = "scoring", callBackData = () => {
  }
                           }) => {

  const [show, setShow] = useContext(CoreModalContext);
  const [dirName, setDirName] = useState("");
  const [folders, setFolders] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [state, dispatch] = useReducer(reducerUpload, defaultStateUpload);

  const _types = getAcceptesTypes(accept);

  const dropzoneOptions = {
    accept: _types,
    maxSize: 1024 * 1024 * 5, // 5 MB
    onDrop: (acceptedFiles) => {
      console.log("Files dropped:", acceptedFiles);
      setUploadedFiles(acceptedFiles)
    }
  };

  let acceptedFiles, getRootProps, getInputProps, isFocused, isDragAccept, isDragReject;
  ( {
    acceptedFiles,
    getRootProps,
    getInputProps,
    isFocused,
    isDragAccept,
    isDragReject
  } = useDropzone(dropzoneOptions) );

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
    if (uploadedFiles.length) {
      uploadFiles();
    }
  }, [uploadedFiles]);

  useEffect(() => {
    if (show.modalUploadFolder) {
    }
  }, [show]);


  async function _uploadFiles(chunks, target_infofiles, dirName, dispatch, enqueueSnackbar) {

    for (let i = 0; i < chunks.length; i++) {
      if (dirName) {
        chunks[i].append("projectName", dirName);
      }
      chunks[i].append("pos", i * target_infofiles);
      await axiosConfig.holder.post("/api/project/upload/", chunks[i], {
        headers: { "Content-Type": "multipart/form-data" }
      }).then((response) => {
        dispatch({ type: actionTypes.FINISH_UPLOAD });
        if (response.data.success) {
          showSuccessBar(enqueueSnackbar, `Successfully uploaded ${ response.data.files } File(s)`);
          return true
        } else {
          dispatch({ type: actionTypes.FAILED_UPLOAD, payload: "An Error occurred. Please contact an admin!" });
          showErrorBar(enqueueSnackbar, "Error while uploading!");
          return false
        }
      }).catch((error) => {
        dispatch({ type: actionTypes.FAILED_UPLOAD, payload: "An Error occurred. Please contact an admin!" });
        if (error.response) {
          console.error(error.response.data);
        } else {
          console.error(error);
        }
        return false
      });
      console.log(i, "=>", chunks[i])
    }
    return true
  }

  // Function to find chunks based on "infofile.txt" occurrences
  const chunkFiles = (files, occurrence = 15) => {
    let chunks = [];
    let formData = new FormData();
    let infoFileCount = 0;

    acceptedFiles.map((file, index) => {
      formData.append(`files${ index }`, file, file.name);
      if (file.name === "infofile.txt") {
        infoFileCount++;
      }

      if (infoFileCount === occurrence) {
        chunks.push(formData);
        formData = new FormData();
        infoFileCount = 0; // Reset for the next chunk
      }
    });

    let keys = 0
    for (const key of formData.keys()) {
      keys += 1;
    }
    if (keys > 0) {
      chunks.push(formData);
    }

    return chunks;
  };

  async function uploadFiles() {
    const target_infofiles = 15
    let chunks = chunkFiles(acceptedFiles, target_infofiles);

    dispatch({ type: actionTypes.START_UPLOADS, payload: chunks.length });

    await _uploadFiles(chunks, target_infofiles, dirName, dispatch, enqueueSnackbar);

    showSuccessBar(enqueueSnackbar, `Upload finished!`);
    handleClose();
    setUploadedFiles([])
    dispatch({ type: actionTypes.SET_RESET });
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
          { state.uploading ? <Row><LoadingIcon/></Row> :
            ( <>
              <Row className={ "pb-3" }>
                <Col>
                  { state.error && <h3 className={ "text-danger" }>{ state.error }</h3> }
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
                          <input { ...getInputProps() } webkitdirectory="true" directory="true" multiple/>
                          <p>Drag 'n' drop some files here, or click to select files</p>
                        </div>
                      </Form.Group>
                    ) ) }
                </Col>
              </Row>
            </> ) }
        </Modal.Body>

        <Modal.Footer>
          <Button variant="secondary" onClick={ handleClose }>Close</Button>
        </Modal.Footer>
      </Modal>
    </Form>
  );
};
export default UploadFolderModal;
