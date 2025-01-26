import React, { useEffect, useState } from "react";
import { useParams } from "react-router";

import { Col, Row } from "react-bootstrap";
import { Gallery } from "react-photoswipe-gallery";
import BoxContainer from "../ui/BoxContainer";
import UselessImageGalleryHolder from "../ui/UselessImageGalleryHolder";

import axiosConfig from "../../axiosConfig";

import { useAuth } from "../../../hooks/CoreAuthProvider";

const UselessImageFilesView = () => {

  const { id } = useParams();
  const [imageFiles, setImageFiles] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const auth = useAuth();

  async function fetchData() {
    await axiosConfig.perform_get(auth, `/api/project/${ id }/get-useless/`, (response) => {
      setImageFiles(response.data);
      setIsLoading(false);
      console.log("Found Images:", response.data);
    });
  }

  useEffect(() => {
    console.log("fetchData");
    fetchData();
  }, []);


  return (
    <>
      { !isLoading && (
        <BoxContainer title={ "Images marked as useless" }>
          <Row>
            { imageFiles.length === 0 ? (
              <Col>There are no images marked as "useless" in this project yet!</Col>
            ) : (
              <Gallery>
                { imageFiles.map((imagefile) => {
                  return <UselessImageGalleryHolder key={ imagefile.id }
                                                    imagefile={ imagefile }
                  />;
                }) }
              </Gallery>
            ) }
          </Row>
        </BoxContainer>
      ) }
    </>
  );
};
export default UselessImageFilesView;
