import React, { useState } from "react";
import { FormControlLabel, Switch } from "@mui/material";
import Offcanvas from "react-bootstrap/Offcanvas";
import DataTable from "react-data-table-component";
import ScoreInfo from "./ScoreInfo";
import { Form } from "react-bootstrap";
import { columnScores, conditionalScoreRowStyles } from "../../helper";
// import "../ui/css/ScorePanel.css";

const ScorePanel = ({ images, show, handleClose }) => {

  const [hideCompleted, setHideCompleted] = useState(true);

  const getFilteredScores = () => {
    if (!hideCompleted) {
      return images.history
    }
    return images.history.filter(score => score.is_completed !== true)
  }

  return (
    <Offcanvas show={ show } onHide={ handleClose } placement={ "end" } name={ "Scoring History" }>
      <Offcanvas.Header closeButton>
        <Offcanvas.Title>Scoring History</Offcanvas.Title>
      </Offcanvas.Header>
      <Offcanvas.Body>
        <Form.Group controlId="formHide" className={"pb-3"}>
          <FormControlLabel
            control={ <Switch checked={ hideCompleted }
                              onChange={ (e) => setHideCompleted(e.target.checked) }
                              name="hideCompleted" /> }
            label="Hide completed?"
          />
        </Form.Group>

        <DataTable
          columns={ columnScores }
          conditionalRowStyles={ conditionalScoreRowStyles }
          data={ getFilteredScores() }
          highlightOnHover
          defaultSortFieldId={ 2 }
          defaultSortAsc={ false }
          fixedHeader={ true }
          allowOverflow={ false }
          theme="dark"
          />


        { images.history && images.history.map(score => {
          if (hideCompleted && score.is_completed) {
            return
          }
          return <ScoreInfo images={ images }
                            score={ score }
                            key={ `sc-info-${ score.id }` }/>;
        }) }
      </Offcanvas.Body>
    </Offcanvas>
  );
};

export default ScorePanel;
