import React, { useEffect, useState } from "react";
import { useParams } from "react-router";

import { useSnackbar } from "notistack";
import { Row } from "react-bootstrap";
import { Gallery } from "react-photoswipe-gallery";
import BoxContainer from "../ui/BoxContainer";
import ImageGalleryHolder from "../ui/ImageGalleryHolder";

import 'photoswipe/dist/photoswipe.css';
import 'photoswipe/dist/default-skin/default-skin.css';
import axiosConfig from "../../axiosConfig";

const UselessImageFilesView = () => {

  const { id } = useParams();
  const [imageFiles, setImageFiles] = useState([]);
  const { enqueueSnackbar } = useSnackbar();

  async function fetchData() {
    const result = await axiosConfig.holder.get(`/api/project/${ id }/get-useless`);
    setImageFiles(result.data);
    console.log("Found Images:", result.data);
  }

  useEffect(() => {
    console.log("fetchData");
    fetchData();

  }, []);


  return (
    <>
      <BoxContainer title={ "Images marked as useless" }>
        <Row>
          <Gallery>
            { imageFiles.map((imagefile) => {
              return <ImageGalleryHolder  key={ imagefile.id }
                                          imagefile={ imagefile }
                                          />;
            }) }
          </Gallery>
        </Row>
      </BoxContainer>
    </>

  );
};

export default UselessImageFilesView;
