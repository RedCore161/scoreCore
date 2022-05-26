import React, { useEffect, useLayoutEffect, useState } from "react";

import BoxContainer from "../ui/BoxContainer";
import { Row } from "react-bootstrap";
import axiosConfig from "../../axiosConfig";
import { fetchImagesAll} from "../../helper";

import { useParams } from "react-router";
import { Gallery } from "react-photoswipe-gallery";
import DifferencesImageGalleryHolder from "../ui/DifferencesImageGalleryHolder";
import LoadingIcon from "../ui/LoadingIcon";
import CorePaginator from "../ui/CorePaginator";

const ProjectDifferencesView = () => {

  const { id } = useParams();

  const [data, setData] = useState({});
  const [pages, setPages] = useState({"varianzes": 1});

  useEffect(() => {
    if ("varianzes" in pages) {
      axiosConfig.getInstance.refreshData();
      fetchImagesAll(id, pages.varianzes).then((data) => {
        setData(data);
      })
    }
  }, [pages]);


  const handlePaginator = ({ selected }) => {
    setPages({...pages, "varianzes":  selected + 1});
  };

  return (
    data ? (
      <>
        <BoxContainer title={`Differences for Project '${data.project}'`}>
          { <CorePaginator pages={ data.pages }
                           handleChangePage={ handlePaginator } /> }

          <Row>
            <Gallery>
              { "elements" in data && data.elements.map((imagefile) => {
                return <DifferencesImageGalleryHolder key={`diff-imagefile-${ imagefile.id }`}
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
