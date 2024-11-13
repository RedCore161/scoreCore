import React from "react";
import { Button, Col, Container, Row } from "react-bootstrap";
import { showErrorBar, showSuccessBar } from "./Snackbar";
import { useSnackbar } from "notistack";

import axiosConfig from "../../axiosConfig";
import "./css/ImageGalleryHolder.css"
import useAuthHeader from "react-auth-kit/hooks/useAuthHeader";


const UselessImageGalleryHolderOverlay = ({ imageId, reloadCallback }) => {

  const { enqueueSnackbar } = useSnackbar();
  const authHeader = useAuthHeader();

  async function removeUseless(imageId) {
    axiosConfig.updateToken(authHeader());
    await axiosConfig.holder.post(`/api/imagescore/${ imageId }/restore/`,)
      .then((response) => {
        if (response.data) {
          if (response.data.success) {
            showSuccessBar(enqueueSnackbar, "Useless-Marking removed!");
            reloadCallback()
          }
        } else {
          showErrorBar(enqueueSnackbar, "Couldn't remove Useless-Marking!");
        }
      }, (error) => {
        if (error.response) {
          console.error(error.response.data);
        } else {
          console.error(error);
        }
      });
  }

  async function acceptAsUseless(imageId) {
    axiosConfig.updateToken(authHeader());
    await axiosConfig.holder.post(`/api/imagescore/${ imageId }/hide/`,)
      .then((response) => {
        if (response.data) {
          if (response.data.success) {
            showSuccessBar(enqueueSnackbar, "Image was Deleted!");
            reloadCallback()
          }
        } else {
          showErrorBar(enqueueSnackbar, "Couldn't delete Image!");
        }
      }, (error) => {
        if (error.response) {
          console.error(error.response.data);
        } else {
          console.error(error);
        }
      });
  }


  return (
    <div className={"actionOpener"} >
      <i className="bi bi-gear-fill text-warning table-icon"/>
      <Container className={"hiddenContent imageOverLay align-bottom"}>

        <Row className={ "mt-5" }><Col>
          <Button variant="success" className={ "my-1 w-100" }
                  onClick={() => removeUseless(imageId)}>Is is useable!</Button>
        </Col></Row>
        <Row><Col>
          <Button variant="danger" className={ "my-1 w-100" }
                  onClick={() => acceptAsUseless(imageId)}>Accept Uselessness</Button>
        </Col></Row>
      </Container>
    </div>
  );
};

export default UselessImageGalleryHolderOverlay;
