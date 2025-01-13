import React, { useState } from "react";
import { Button, Col, Container, Form, InputGroup, Row } from "react-bootstrap";
import { useSearchParams } from "react-router-dom";
import { useForm } from "react-hook-form";
import { useAuth } from "../../../hooks/CoreAuthProvider";

const LoginForm = () => {

  const [searchParams, setSearchParams] = useSearchParams();

  const { register, handleSubmit } = useForm();
  const [showPasswd, setShowPasswd] = useState(false);

  const onSubmit = async (data) => {
    const auth = useAuth();
    const forward = searchParams.get('forward') || '/project/overview/';
    await auth.loginAction(data, forward);
  };

  return (
    <Container>
      <Row
        md={ 4 }
        className="justify-content-md-center"
        style={ { marginTop: 60 } }
      >
        <Col xs={ 6 }>
          <Form onSubmit={ handleSubmit(onSubmit) }>
            <Form.Group controlId="formUser">
              <Form.Label>Username</Form.Label>
              <Form.Control
                type="text"
                placeholder="Enter User"
                { ...register('username') }
              />
            </Form.Group>

            <Form.Group controlId="formPassword" className={ 'mt-4' }>
              <Form.Label>Password</Form.Label>
              <InputGroup>
                <Form.Control
                  type={ showPasswd ? 'text' : 'password' }
                  placeholder="Password"
                  { ...register('password') }
                />
                <InputGroup.Text>
                  <i
                    onClick={ () => setShowPasswd(!showPasswd) }
                    className={ showPasswd ? 'bi bi-eye-slash' : 'bi bi-eye' }
                  />
                </InputGroup.Text>
              </InputGroup>
            </Form.Group>

            <Button variant="primary" type="submit" className={ 'mt-5' }>
              Login
            </Button>
          </Form>
        </Col>
      </Row>
    </Container>
  );
};
export default LoginForm;
