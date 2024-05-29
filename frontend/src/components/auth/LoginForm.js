import React, { useState } from 'react';
import { Button, Col, Container, Form, InputGroup, Row } from "react-bootstrap";
import { useForm } from "react-hook-form";
import axios from "axios";
import { useNavigate } from "react-router";
import { useSignIn } from "react-auth-kit";
import { jwtDecode } from "jwt-decode";
import { useSearchParams } from "react-router-dom";
import { useSnackbar } from "notistack";
import { showErrorBar } from "../ui/Snackbar";

const LoginForm = () => {

  const liveTime = process.env.REACT_APP_LOGIN_TIME | 3600

  const signIn = useSignIn()
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [showPasswd, setShowPasswd] = useState(false);

  const { enqueueSnackbar } = useSnackbar();
  const { register, handleSubmit } = useForm();

  const onSubmit = async (data) => {
    try {
      const response = await axios.post(
        `${ process.env.REACT_APP_BACKEND_URL }/api/token/`,
        data
      );
      signIn({
        token: response.data.access,
        expiresIn: liveTime,
        tokenType: "Bearer",
        refreshToken: response.data.refresh,
        refreshTokenExpireIn: liveTime * 2,
        authState: jwtDecode(response.data.access),
      });

      const forward = searchParams.get("forward") || "/";
      navigate(forward);

    } catch (err) {
      console.log("Error: ", err);
      showErrorBar(enqueueSnackbar, "Login failed!");
    }
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

            <Button variant="primary" type="submit" className={ "mt-5" }>
              Login
            </Button>

          </Form>
        </Col>
      </Row>
    </Container>
  );
};
export default LoginForm;

