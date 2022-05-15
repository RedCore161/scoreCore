import React, { useLayoutEffect, useState } from "react";
import { Button, Col, Row } from "react-bootstrap";
import { fetchBackups } from "../../helper";
import BoxContainer from "../ui/BoxContainer";
import LoadingIcon from "../ui/LoadingIcon";

const BackupView = () => {

  const [data, setData] = useState([]);

  useLayoutEffect(() => {
    fetchBackups().then((response) => {
      setData(response)
    });
  }, []);


  return (
    data ? (
      <BoxContainer title="Available Backups">
        <Row>
          { 'elements' in data && data.elements.map((backup) => {
            return <Col md={4} key={backup.id}>
              <Button>{backup.name}</Button>
            </Col>;
          }) }
        </Row>
      </BoxContainer>
    ) : (<Row><LoadingIcon /></Row> )
  );
};

export default BackupView;
