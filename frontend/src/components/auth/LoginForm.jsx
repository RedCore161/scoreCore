import React, { useState } from "react";
import { Button, Col, Container, Form, InputGroup, Row } from "react-bootstrap";
import axios from "axios";
import { useNavigate, useSearchParams } from "react-router-dom";
import useSignIn from "react-auth-kit/hooks/useSignIn";
import { useForm } from "react-hook-form";
import { jwtDecode } from "jwt-decode";
import { showErrorBar } from "../ui/Snackbar";
import { useSnackbar } from "notistack";


const LoginForm = (_) => {

  const signIn = useSignIn()
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const { enqueueSnackbar } = useSnackbar();
  const { register, handleSubmit } = useForm();
  const [showPasswd, setShowPasswd] = useState(false);

  const onSubmit = async (data) => {
    const forward = searchParams.get("forward") || "/";
    await axios.post(
      `${ process.env.REACT_APP_BACKEND_URL }/api/token/`,
      data
    ).then((response) => {
      if (signIn({
        auth: {
          token: response.data.access,
          type: "Bearer"
        },
        refresh: response.data.refresh,
        userState: jwtDecode(response.data.access)
      })) {
        navigate(forward);
      } else {
        showErrorBar(enqueueSnackbar, "Login failed!");
      }
    }, (error) => {
      showErrorBar(enqueueSnackbar, "Login failed!");
    });
  };

  return (
    <Container>
      <Row md={ 4 } className="justify-content-md-center" style={ { "marginTop": 60 } }>
        <Col xs={ 6 }>
          <Form onSubmit={ handleSubmit(onSubmit) }>
            <Form.Group controlId="formUser">
              <Form.Label>Username</Form.Label>
              <Form.Control type="text" placeholder="Enter User" { ...register("username") } />
            </Form.Group>

            <Form.Group controlId="formPassword" className={ "mt-4" }>
              <Form.Label>Password</Form.Label>
              <InputGroup>
                <Form.Control type={ showPasswd ? "text" : "password" } placeholder="Password" { ...register("password") } />
                <InputGroup.Text>
                  <i onClick={() => setShowPasswd(!showPasswd)} className={ showPasswd ? "bi bi-eye-slash" : "bi bi-eye" }/>
                </InputGroup.Text>
              </InputGroup>
            </Form.Group>

            <Button variant="primary" type="submit" className={ "mt-5" } >
              Login
            </Button>

          </Form>
        </Col>
      </Row>
    </Container>
  );
};
export default LoginForm;
