import React, { useContext, useState } from 'react';
import { Button, Form, Modal } from "react-bootstrap";
import { CoreModalContext } from "./coreModalContext";
import { useEffect } from "react";
import { useForm } from "react-hook-form";

import { Typeahead } from "react-bootstrap-typeahead";
import axiosConfig from "../../axiosConfig";
import { configText, configTextNeeded } from "../form/config";
import "../ui/css/CustomModal.css"

const icons = ["🐵","🐶","🐱","🐷","🐭","🐰"]
const defaultForm = {
  name: "",
  icon: "",
  features: "",
};

const CreateProjectModal = ( {callBackData = () => {}} ) => {
  const { control, register, formState: { errors }, setValue, handleSubmit, reset } = useForm({ defaultValues: defaultForm });
  const [show, setShow] = useContext(CoreModalContext)
  const [folders, setFolders] = useState([]);
  const [folder, setFolder] = useState([]);

  const handleClose = () => {
    setShow((show) => ( { ...show, modalProjectModal: false } ))
    reset(defaultForm)
    setFolder([])
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
    console.log("FOLDER", folder);
    axiosConfig.holder.post(`/api/project/create/`, {
      ...data,
      folder: folder[0].name,
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


  function isDisabledYet() {
    return false; //TODO
  }

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
            <Form.Control type="text" placeholder="Project name" { ...register("name", configTextNeeded) } />
          </Form.Group>

          <Form.Group controlId="formIcon">
            <Form.Label>
              Icon 📷 (Suggestions: {icons.map((ic, _i) => {
                return <span key={`sug-sp-${_i}`} onClick={() => setValue("icon", ic)}>{ic}</span>
              })})
              <div className={ "modalErrors" }>
                { errors.icon?.type === "required" && errors.icon?.message }
              </div>
            </Form.Label>
            <Form.Control className="w-25" type="text" width={ 5 } placeholder="Icon" { ...register("icon", configText) } />
          </Form.Group>

          <Form.Group controlId="formFolder" className={ "mb-4" }>
            <Form.Label>Folder 📂</Form.Label>
            <Typeahead
              id="folder-chooser"
              labelKey={ opt => `${opt.name} Images: ${opt.images} ${opt.in_use === true && ", 📌"}` }
              onChange={ setFolder }
              selected={ folder }
              options={ folders?.data ? folders.data : [] }
              placeholder="Select a folder..."
              theme="dark"
              clearButton
            />
          </Form.Group>

          <Form.Group controlId="formFeature">
            <Form.Label>
              Features
              <div className={ "modalErrors" }>
                { errors.features?.type === "required" && errors.features?.message }
                { errors.features?.type === "minLength" && errors.features?.message }
              </div>
            </Form.Label>
            <Form.Control type="text" placeholder="Rateable features (comma seperated)"
                          { ...register("features", configTextNeeded) } />
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
