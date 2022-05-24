import React from "react";
import { Col, Container, Row } from "react-bootstrap";

import "./css/DifferencesImageGalleryHolderOverlay.css";


const DifferencesImageGalleryHolderOverlay = ({ imagefile }) => {

  const elements = [
    { "name": "File", "value": imagefile.filename },
    { "name": "Eyes", "value": imagefile.varianz_eye ? imagefile.varianz_eye.toFixed(2) : 0 },
    { "name": "Nose", "value": imagefile.varianz_nose ? imagefile.varianz_nose.toFixed(2) : 0 },
    { "name": "Cheeks", "value": imagefile.varianz_cheek ? imagefile.varianz_cheek.toFixed(2) : 0 },
    { "name": "Ears", "value": imagefile.varianz_ear ? imagefile.varianz_ear.toFixed(2) : 0 },
    { "name": "Whiskers", "value": imagefile.varianz_whiskers ? imagefile.varianz_whiskers.toFixed(2) : 0 },
    { "name": "Total-Score", "value": imagefile.varianz ? imagefile.varianz.toFixed(2) : 0 },
  ];


  function getDifferences(value) {
    if (value === 0) {
      return "text-success";
    }

    if (value > 2) {
      return "text-danger";
    }

    if (value > 1) {
      return "text-warning";
    }
    return "";
  }

  return (
    <div className={ "actionOpener" }>
      <i className="bi bi-gear-fill text-warning table-icon"/>
      <Container className={ "hiddenContent imageOverLay pt-5" }>

        { elements.map((element) =>
          <Row className={ `${ getDifferences(element.value) }` }>
            <Col md={ 6 }>{ element.name }:</Col>
            <Col>{ element.value }</Col>
          </Row>
        ) }

      </Container>
    </div>
  );
};

export default DifferencesImageGalleryHolderOverlay;
