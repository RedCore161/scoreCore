import React, { useState } from "react";
import { FormControlLabel, Switch } from "@mui/material";
import DataTable from "react-data-table-component";
import { Col, Form, Row } from "react-bootstrap";
import { columnScores, conditionalScoreRowStyles } from "../../helper";
// import "../ui/css/ScorePanel.css";

const ScorePanel = ({ images, callback }) => {

  const [hideCompleted, setHideCompleted] = useState(true);

  const getFilteredScores = () => {
    if (!hideCompleted) {
      return images.history;
    }
    return images.history.filter(score => score.is_completed !== true);
  };

  return (
    <>
      <Row className={ "mt-2 pb-2" } id={ `counter-${ images.files_left }` }>
        <Col className={ "mt-2" } md={ 4 }>
          Images left: { images.files_left }
        </Col>
        <Col>
          <Form.Group controlId="formHide">
            <FormControlLabel
              control={ <Switch checked={ hideCompleted }
                                onChange={ (e) => setHideCompleted(e.target.checked) }
                                name="hideCompleted"/> }
              label="Hide completed?"
            />
          </Form.Group>
        </Col>
      </Row>

      <DataTable
        columns={ columnScores }
        conditionalRowStyles={ conditionalScoreRowStyles }
        data={ getFilteredScores() }
        highlightOnHover
        defaultSortFieldId={ 3 }
        defaultSortAsc={ false }
        onRowClicked={(row) => callback({ file: row.file})}
        fixedHeader={ true }
        allowOverflow={ false }
        theme="dark"
      />

    </>
  );
};

export default ScorePanel;
