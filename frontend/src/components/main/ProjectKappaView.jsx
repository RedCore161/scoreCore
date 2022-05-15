import React, { useLayoutEffect, useState } from "react";

import BoxContainer from "../ui/BoxContainer";
import { Button, Col, Row } from "react-bootstrap";
import ProjectCardView from "../ui/ProjectCardView";
import axiosConfig from "../../axiosConfig";
import { fetchImages, fetchProjects, SelectListened } from "../../helper";
import { showErrorBar, showSuccessBar } from "../ui/Snackbar";
import * as actionTypes from "../reducer/reducerTypes";
import { useSnackbar } from "notistack";
import { useParams } from "react-router";

const ProjectKappaView = () => {

  const { id } = useParams();

  const [images, setImages] = useState([]);
  const { enqueueSnackbar } = useSnackbar();

  useLayoutEffect(() => {
    axiosConfig.getInstance.refreshData();
    fetchImages(id).then((images) => {
      setImages(images);
    })
  }, []);


  return (
    images && (
      <>
        <BoxContainer title={`Kapp' for Project '${2}'`}>

        </BoxContainer>
      </>
    )
  );
};

export default ProjectKappaView;
