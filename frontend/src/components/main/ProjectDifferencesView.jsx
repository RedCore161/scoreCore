import React, { useEffect, useState } from "react";

import BoxContainer from "../ui/BoxContainer";
import { Button, Col, Row } from "react-bootstrap";
import axiosConfig from "../../axiosConfig";
import { fetchImagesAll } from "../../helper";

import { useParams } from "react-router";
import { Gallery } from "react-photoswipe-gallery";
import DifferencesImageGalleryHolder from "../ui/DifferencesImageGalleryHolder";
import LoadingIcon from "../ui/LoadingIcon";
import CorePaginator from "../ui/CorePaginator";
import { showSuccessBar } from "../ui/Snackbar";
import { useSnackbar } from "notistack";
import useAuthHeader from "react-auth-kit/hooks/useAuthHeader";

const ProjectDifferencesView = () => {

  const { id } = useParams();

  const [data, setData] = useState({});
  const [pages, setPages] = useState({ "stddevs": 1 });
  const { enqueueSnackbar } = useSnackbar();
  const authHeader = useAuthHeader();

  useEffect(() => {
    if ("stddevs" in pages) {
      axiosConfig.updateToken(authHeader());
      fetchImagesAll(id, pages.stddevs).then((data) => {
        setData(data);
      });
    }
  }, [pages]);

  const handlePaginator = ({ selected }) => {
    setPages({ ...pages, "stddevs": selected + 1 });
  };

  async function recalcuateStdDev() {
    axiosConfig.updateToken(authHeader());
    await axiosConfig.holder.get(`/api/project/${ id }/recalculate-stddev/`)
      .then((response) => {
        if (response.data) {
          if (response.data.success) {
            showSuccessBar(enqueueSnackbar, "Successfully recalculated!");
            fetchImagesAll(id, pages.stddevs).then((data) => {
              setData(data);
            });
          }
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
    data ? (
      <>
        <BoxContainer title={ "Actions" }>
          <Row>
            <Col>
              <Button variant={ "success" } onClick={ () => recalcuateStdDev() }>Recalculate Std-Deviation</Button>
            </Col>
          </Row>
        </BoxContainer>
        <BoxContainer title={ `Differences for Project '${ data.project }' with ${ data.usersCount } Users and ${ data.scoresCount} Scores` }>
          { <CorePaginator pages={ data.pages }
                           handleChangePage={ handlePaginator }/> }

          <Row>
            <Gallery>
              { "elements" in data && data.elements.map((imagefile) => {
                return <DifferencesImageGalleryHolder key={ `diff-imagefile-${ imagefile.id }` }
                                                      imagefile={ imagefile }
                />;
              }) }
            </Gallery>
          </Row>
        </BoxContainer>
      </>
    ) : ( <Row><LoadingIcon/></Row> )
  );
};
export default ProjectDifferencesView;
