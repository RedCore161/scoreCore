import React from "react";
import { Button, Col, Container, Row } from "react-bootstrap";
import { showErrorBar, showSuccessBar } from "./Snackbar";
import { useSnackbar } from "notistack";


import "./css/DifferencesImageGalleryHolderOverlay.css";


const DifferencesImageGalleryHolderOverlay = ({ imagefile, reloadCallback }) => {

  const { enqueueSnackbar } = useSnackbar();
  const elements = [
    { "name": "File", "value": imagefile.filename },
    { "name": "Eyes", "value": imagefile.diversity_eye ? imagefile.diversity_eye.toFixed(2) : 0 },
    { "name": "Nose", "value": imagefile.diversity_nose ? imagefile.diversity_nose.toFixed(2) : 0 },
    { "name": "Cheeks", "value": imagefile.diversity_cheek ? imagefile.diversity_cheek.toFixed(2) : 0 },
    { "name": "Ears", "value": imagefile.diversity_ear ? imagefile.diversity_ear.toFixed(2) : 0 },
    { "name": "Whiskers", "value": imagefile.diversity_whiskers ? imagefile.diversity_whiskers.toFixed(2) : 0 },
    { "name": "Total-Score", "value": imagefile.diversity ? imagefile.diversity.toFixed(2) : 0 },
  ];

  console.log("XXX", typeof imagefile.diversity_eye);

  function getDifferences(value) {
    if (value === 0) {
      return "text-success";
    }
    if (value > 6) {
      return "text-danger";
    }

    if (value > 3) {
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
