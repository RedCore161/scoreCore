import React, { useContext } from 'react';
import { Button, Form, Modal } from "react-bootstrap";
import { CoreModalContext } from "./coreModalContext";
import { useRef, useEffect } from "react";

import "../ui/css/CustomModal.css"

const ShowTextModal = (  ) => {

  const [show, setShow] = useContext(CoreModalContext)
  const textArea = useRef();
  const handleClose = () => {
    setShow((show) => ( { ...show, modalShowText: false } ))
  }

  const handleFocus = (event) => event.target.select();

  useEffect(() => {
    const area = textArea.current;
    if (area) {
      area.scrollTop = area.scrollHeight;
    }
  }, [show]);

  return (
    <Form>
      <Modal show={ show.modalShowText } onHide={ handleClose } dialogClassName={ "wide-modal" } >
        <Modal.Header>
          <Modal.Title>{ show.title }</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form.Group controlId="formName">
            <Form.Label>Content</Form.Label>
            <Form.Control as="textarea"
                          ref={ textArea }
                          rows={ 15 }
                          value={ show.txt }
                          readOnly={ true }
                          onFocus={handleFocus} />
          </Form.Group>
        </Modal.Body>

        <Modal.Footer>
          <Button variant="secondary" onClick={ handleClose }>Close</Button>
        </Modal.Footer>
      </Modal>
    </Form>
  );
};
export default ShowTextModal;
