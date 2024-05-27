import React from "react";
import { Col } from "react-bootstrap";
import { Item } from "react-photoswipe-gallery";
import { Element } from "react-scroll";

import UselessImageGalleryHolderOverlay from "./UselessImageGalleryHolderOverlay";

import "./css/ImageGalleryHolder.css";


const UselessImageGalleryHolder = ({ overlaySetter, imagefile }) => {

  const path = [process.env.REACT_APP_BACKEND_URL, "media", imagefile.path, imagefile.filename].join("/")

  const reloadCallback = () => {
    window.location.reload(true);
  };

  return (
    <Col className={ "my-3" } md={ 3 }>
      <Element name={ `imagefile-${ imagefile.id }` } className="element">
        <div className={ `imageHolder` }>
          <Item key={ imagefile.id }
                original={ path }
                width={ 340 }
                height={ 340 }>

                { ({ ref, open }) => (
                  <>

                    <img key={ imagefile.id } src={ path } className="img-fluid drawLayer" data-image={ path }
                         ref={ ref } onClick={ open } title={ `${ imagefile.filename }` } alt={ imagefile.id }
                         width={ 340 } height={ 340 }/>

                    <UselessImageGalleryHolderOverlay imageId={ imagefile.id }
                                                      overlaySetter={ overlaySetter }
                                                      reloadCallback={ reloadCallback }

                    />

                  </>
                ) }
          </Item>
        </div>
      </Element>
    </Col>
  );
};

export default UselessImageGalleryHolder;
