import React from "react";
import ReactPaginate from "react-paginate";

const CorePaginator = ({ pages, handleChange }) => {

  return (
    <span className={ "paginatorContainer" }>
      <div className={ "paginatorContent" }>
        <ReactPaginate
          nextLabel={ "»" }
          previousLabel={ "«" }
          breakLabel={ "..." }
          breakClassName={ "page-item" }
          breakLinkClassName={ "page-link" }
          pageCount={ pages }
          onPageChange={ handleChange }
          onPageActive={ handleChange }
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
  );

};

export default CorePaginator;
