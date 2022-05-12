import {Card} from "react-bootstrap";
import React from "react";

const BoxContainer = ({title, children}) => {
    return (
        <Card className="col-* my-4">
            <Card.Body>
                <Card.Title className="card-header">{ title }</Card.Title>
                <Card.Text as="div">
                    { children }
                </Card.Text>
            </Card.Body>
        </Card>
    );
};

export default BoxContainer;
