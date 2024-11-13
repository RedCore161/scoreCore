import React, { useState } from "react";
import { FormControlLabel, Switch } from "@mui/material";
import DataTable from "react-data-table-component";
import { Col, Form, Row } from "react-bootstrap";
import { conditionalScoreRowStyles } from "../../helper";
import { columnScores } from "../../unfinishColumns";

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
      <Row className={ "my-2 pb-2" } id={ `counter-${ images.files_left }` }>
        <Col className={ "mt-2" } sm={ 4 }>
          <div>Images left:</div>
          <div>Scores target:</div>
          <div>Scores finished:</div>
          <div>Scores started:</div>
        </Col>
        <Col className={ "mt-2" } sm={ 3 }>
          <div>{ images.files_left }</div>
          <div>🚩 { images.score_desired }</div>
          <div>✔ { images.score_finished }</div>
          <div>⭕ { images.score_started - images.score_finished }</div>
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
        onRowClicked={ (row) => callback({ file: row.file }) }
        fixedHeader={ true }
        allowOverflow={ false }
        theme="dark" />
    </>
  );
};
export default ScorePanel;
