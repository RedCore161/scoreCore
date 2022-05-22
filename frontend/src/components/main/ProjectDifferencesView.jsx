import React, { useLayoutEffect, useState } from "react";

import BoxContainer from "../ui/BoxContainer";
import { Row } from "react-bootstrap";
import axiosConfig from "../../axiosConfig";
import { fetchImagesAll} from "../../helper";

import { useSnackbar } from "notistack";
import { useParams } from "react-router";
import { Gallery } from "react-photoswipe-gallery";
import DifferencesImageGalleryHolder from "../ui/DifferencesImageGalleryHolder";

const ProjectDifferencesView = () => {

  const { id } = useParams();

  const [images, setImages] = useState([]);
  const { enqueueSnackbar } = useSnackbar();

  useLayoutEffect(() => {
    axiosConfig.getInstance.refreshData();
    fetchImagesAll(id).then((images) => {
      console.log("images", images);
      setImages(images);
    })
  }, []);


  return (
    images && (
      <>
        <BoxContainer title={`Differences for Project '${images.project}'`}>
          <Row>
            <Gallery>
              { "images" in images && images.images.map((imagefile) => {
                return <DifferencesImageGalleryHolder key={ imagefile.id }
                                                      imagefile={ imagefile }
                />;
              }) }
            </Gallery>
          </Row>
        </BoxContainer>
      </>
    )
  );
};

export default ProjectDifferencesView;
