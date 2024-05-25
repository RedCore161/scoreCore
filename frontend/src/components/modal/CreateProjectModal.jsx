import React, { useContext } from 'react';
import { Button, Form, Modal } from "react-bootstrap";
import { CoreModalContext } from "./coreModalContext";
import { useEffect } from "react";

import "../ui/css/CustomModal.css"
import { Typeahead } from "react-bootstrap-typeahead";
import axiosConfig from "../../axiosConfig";
import { configTextNeeded } from "../form/config";

const defaultForm = {
  name: "",
  folder: "",
  features: "",
};


const CreateProjectModal = (  ) => {
  const { control, register, formState: { errors }, handleSubmit, reset } = useForm({ defaultValues: defaultForm });
  const [show, setShow] = useContext(CoreModalContext)
  const [folders, setFolders] = useState([]);
  const [folder, setFolder] = useState([]);

  const handleClose = () => {
    setShow((show) => ( { ...show, modalProjectModal: false } ))
  }

  useEffect(() => {
    if (show.modalProjectModal) {
      fetchFolders();
    }
  }, [show]);

  async function fetchFolders() {
    await axiosConfig.holder.get(`/api/project/available/`).then((response) => {
      setFolders(response.data);
    }, (error) => {
      if (error.response) {
        console.error(error.response.data);
      } else {
        console.error(error);
      }
    });
  }

  const onSubmit = (data) => {
    axiosConfig.holder.post(`/api/project/new/`, {
      ...data,
    }).then((response) => {
      if (response.data.success) {
        console.log(response);
        callBackData(response.data.model);
        handleClose();
      }
    }, (error) => {
      if (error.response) {
        console.log(error.response.data);
      } else {
        console.error(error);
      }
    });
  };


  return (
    <Form>
      <Modal show={ show.modalProjectModal } onHide={ handleClose } dialogClassName={ "wide-modal" } >
        <Modal.Header>
          <Modal.Title>Create New Project</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form.Group controlId="formName">
            <Form.Label>
              Name
              <div className={ "modalErrors" }>
                { errors.name?.type === "required" && errors.name?.message }
                { errors.name?.type === "minLength" && errors.name?.message }
              </div>
            </Form.Label>
            <Form.Control type="text" placeholder="Project name"
                          { ...register("name", configTextNeeded) } />
          </Form.Group>

          <Form.Group controlId="formFolder" className={ "mb-4" }>
            <Form.Label>Folder</Form.Label>
            <Typeahead
              id="folder-chooser"
              labelKey="name"
              onChange={ setFolder }
              selected={ folder }
              options={ folders ? folders : [] }
              placeholder="Select a folder..."
              clearButton={ true }
              theme="dark"
            />
          </Form.Group>

        </Modal.Body>

        <Modal.Footer>
          <Button variant="secondary" onClick={ handleClose }>Close</Button>
          <Button variant="success" onClick={ handleSubmit(onSubmit) } disabled={ isDisabledYet() }>Create</Button>
        </Modal.Footer>
      </Modal>
    </Form>
  );

};

export default CreateProjectModal;
