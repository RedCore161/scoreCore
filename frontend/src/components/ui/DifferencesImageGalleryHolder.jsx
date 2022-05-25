import React from "react";
import { Col } from "react-bootstrap";
import { Item } from "react-photoswipe-gallery";
import { Element } from "react-scroll";

import DifferencesImageGalleryHolderOverlay from "./DifferencesImageGalleryHolderOverlay";

import "./css/ImageGalleryHolder.css";


const DifferencesImageGalleryHolder = ({ overlaySetter, imagefile }) => {

  const path = [process.env.REACT_APP_BACKEND_URL, "media", imagefile.rel_path, imagefile.filename].join("/");

  function getBorderClazz() {

    if (imagefile.varianz === 0) {
      return "success-border"
    }

    if (imagefile.varianz > 1.5) {
      return "failed-border"
    }

    return "warning-border"

  }

  return (
    <Col className={ "my-3" } md={ 3 } >
      <Element name={ `imagefile-${ imagefile.id }` } className="element">
        <div className={ `imageHolder` }>
          <Item key={ imagefile.id }
                original={ path }
                width={ 340 }
                height={ 340 }>

            { ({ ref, open }) => (
              <>
                <img key={ imagefile.id } src={ path } className={`img-fluid drawLayer ${getBorderClazz()}`} data-image={ path }
                     ref={ ref } onClick={ open } title={ `${ imagefile.filename }` } alt={ imagefile.id }
                     width={ 340 } height={ 340 }/>

                <DifferencesImageGalleryHolderOverlay key={`actionOpener-${imagefile.id}`}
                                                      imagefile={ imagefile }
                                                      overlaySetter={ overlaySetter } />

              </>
            ) }
          </Item>
        </div>
      </Element>
    </Col>
  );
};

export default DifferencesImageGalleryHolder;
