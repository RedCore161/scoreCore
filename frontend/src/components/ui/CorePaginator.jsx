import React from "react";
import ReactPaginate from "react-paginate";
import { Col, Row } from "react-bootstrap";

import "../ui/css/CorePaginator.css";

const CorePaginator = ({ pages, handleChangePage, handleChangeSize=()=>{} }) => {

  return (
    <Row>
      <Col md={ 4 }/>
      <Col md={ 4 } align="center">
        <span className={ "paginatorPages" }>
          {/*TODO*/}
        </span>
      </Col>

      <Col md={ 4 }>
        <span className={ "paginatorContainer" }>
          <div className={ "paginatorContent" }>
            <ReactPaginate
              nextLabel={ "»" }
              previousLabel={ "«" }
              breakLabel={ "..." }
              breakClassName={ "page-item" }
              breakLinkClassName={ "page-link" }
              pageCount={ pages }
              onPageChange={ handleChangePage }
              onPageActive={ handleChangePage }
              containerClassName={ "pagination" }
              pageClassName={ "page-item" }
              pageLinkClassName={ "page-link" }
              activeClassName={ "active" }
              nextLinkClassName={ "page-link" }
              previousLinkClassName={ "page-link" }
              nextClassName={ "page-item" }
              previousClassName={ "page-item" }
            />
          </div>
        </span>
      </Col>
    </Row>

  );

};

export default CorePaginator;
