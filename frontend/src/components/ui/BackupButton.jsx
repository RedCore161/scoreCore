import { Button, Col, Row } from "react-bootstrap";
import React from "react";
import "../ui/css/BackupButton.css";

const BackupButton = ({ id, name, callbackRestore, callbackDelete }) => {

  return (
    <Row className={ "p-3 mx-1 my-2 bg-primary backupbutton-row" }>
        <Col md={ 3 } >
          <Button variant={ "outline-success" } className={ " me-2" }
                  onClick={ () => callbackRestore(id, name) }>Restore </Button>
          <Button variant={ "outline-danger" } onClick={ () => callbackDelete(id) }>Delete</Button>
        </Col>
        <Col>
          <a className={ "backupbutton-text" } href={`${process.env.REACT_APP_BACKEND_URL}/media/backup/${name}`}>{ name }</a>
        </Col>
    </Row>
  );
};

export default BackupButton;
