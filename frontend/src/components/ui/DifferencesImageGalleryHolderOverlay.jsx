import React from "react";
import { Button, Col, Container, Row } from "react-bootstrap";

import "./css/DifferencesImageGalleryHolderOverlay.css";
import axiosConfig from "../../axiosConfig";
import { useAuthHeader } from "react-auth-kit";


const DifferencesImageGalleryHolderOverlay = ({ imagefile }) => {

  const elements = getElements()
  const authHeader = useAuthHeader();

  function getElements() {
    let currentId = 10;
    let variances = []
    for (let key in imagefile.data) {
      if (imagefile.data.hasOwnProperty(key)) {
        let val = imagefile.data[key]
        variances.push({
          id: currentId++,
          name: key,
          value: val ? val.toFixed(2) : 0,
          format: true
        });
      }
    }

    return [
      { id: 1, name: "File", value: imagefile.filename, format: false},
      { id: 2, name: "Scorers", value: imagefile.scores.length, format: false },
      ...variances,
      { id: 1000, name: "∑ Std.-Dev.", value: imagefile.variance ? imagefile.variance.toFixed(2) : 0 , format: true },
    ];
  }

  function openHeatMap(event, ) {
    event.stopPropagation();

    const _header = authHeader();
    axiosConfig.updateToken(_header);
    axiosConfig.holder.get(`/api/project/${imagefile.project}/cross-variance/?file_id=${imagefile.id}`, { responseType: "blob"}).then((response) => {
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const newTab = window.open();
      newTab.location = url;
    }, (error) => {
      if (error.response) {
        console.log(error.response.data);
      } else {
        console.error(error);
      }
    });
  }

  function getDifferences(element) {
    if (element.format) {
      if (element.value === 0) {
        return "text-success";
      }

      if (element.value >= 0.5) {
        return "text-danger";
      }

      if (element.value < 0.5) {
        return "text-warning";
      }
    }
    return ""
  }

  return (
    <div className={ "actionOpener" }>
      <i className="bi bi-gear-fill text-warning table-icon"/>
      <Container className={ "hiddenContent imageOverLay pt-5" }>

        { elements.map((element) =>
          <Row className={ `${ getDifferences(element) }` } key={`diff-row-${element.name}`}>
            <Col md={ 6 }>{ element.name.replace(/^variance_/, '') }:</Col>
            <Col>{ element.value }</Col>
          </Row>
        ) }
        <Row className={"mt-2"}>
          <Col>
            <Button variant={"outline-success"} onClick={(e) => openHeatMap(e)}>Open 🔥-Map</Button>
          </Col>
        </Row>

      </Container>
    </div>
  );
};

export default DifferencesImageGalleryHolderOverlay;
