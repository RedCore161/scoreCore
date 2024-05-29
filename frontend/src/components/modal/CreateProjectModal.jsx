import React, { useContext, useState } from 'react';
import { Button, Form, Modal } from "react-bootstrap";
import { CoreModalContext } from "./coreModalContext";
import { useEffect } from "react";
import { useForm } from "react-hook-form";

import { Typeahead } from "react-bootstrap-typeahead";
import axiosConfig from "../../axiosConfig";
import { configText, configTextNeeded } from "../form/config";
import "../ui/css/CustomModal.css"
import { fetchFolders } from "../../helper";

const suggestions = [
  {icon: "🐵"},
  {icon: "🐶"},
  {icon: "🐱"},
  {icon: "🐷"},
  {icon: "🐭", txt: "Eyes, Nose, Cheeks, Ears, Whiskers"},
  {icon: "🐰"}
  ]

const defaultForm = {
  name: "",
  icon: "",
  features: "",
};

const CreateProjectModal = ( {callBackData = () => {}} ) => {
  const { register, formState: { errors }, setValue, setFocus, handleSubmit, reset } = useForm({ defaultValues: defaultForm });
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
      fetchFolders(setFolders);
    }
  }, [show]);


  const onSubmit = (data) => {
    let additonal = {}
    if (folder.length > 0) {
      additonal["folder"] = folder[0].name
    }
    axiosConfig.holder.post(`/api/project/create/`, {
      ...data,
      ...additonal
    }).then((response) => {
      if (response.data.success) {
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


  function advSetValue(_field, _val) {
    setValue(_field, _val,{ shouldTouch: false })
    setFocus(_field, false)
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

          <Form.Group controlId="formIcon" className={"mt-3"}>
            <Form.Label>
              Icon 📷 (Suggestions: {suggestions.map(({ icon }, _i) => {
                return <span key={`sug-sp-${_i}`} onClick={() => advSetValue("icon", icon)}>{icon}</span>
              })})
              <div className={ "modalErrors" }>
                { errors.icon?.type === "required" && errors.icon?.message }
              </div>
            </Form.Label>
            <Form.Control className="ctl-short" type="text" placeholder="Icon" { ...register("icon", configText) } />
          </Form.Group>

          <Form.Group controlId="formFeature" className={ "mt-3" }>
            <Form.Label>
              Features (Suggestions: {suggestions.map((icon, _i) => {
                if (!icon.txt) {
                  return
                }
                return <span key={`sug-fe-${_i}`} onClick={() => advSetValue("features", icon.txt)}>{icon.icon}</span>
              })})
              <div className={ "modalErrors" }>
                { errors.features?.type === "required" && errors.features?.message }
                { errors.features?.type === "minLength" && errors.features?.message }
              </div>
            </Form.Label>
            <Form.Control type="text" placeholder="Rateable features (comma seperated)"
                          { ...register("features", configTextNeeded) } />
          </Form.Group>

          <Form.Group controlId="formFolder" className={ "mt-3" }>
            <Form.Label>Folder 📂 (optional)</Form.Label>
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

        </Modal.Body>

        <Modal.Footer>
          <Button variant="secondary" onClick={ handleClose }>Close</Button>
          <Button variant="success" onClick={ handleSubmit(onSubmit) }>Create</Button>
        </Modal.Footer>
      </Modal>
    </Form>
  );
};
export default CreateProjectModal;
