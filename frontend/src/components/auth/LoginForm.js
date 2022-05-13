import React from 'react';
import {Button, Col, Container, Form, Row} from "react-bootstrap";
import { useForm } from "react-hook-form";
import { connect } from 'react-redux';
import * as actions from '../../store/actions/auth';
import { useSnackbar } from "notistack";

const LoginForm = (props) => {

  const { register, handleSubmit } = useForm();
  const { enqueueSnackbar } = useSnackbar();

  const onSubmit = (data) => {
    props.onAuth(data.user, data.password, enqueueSnackbar);
  };

  return (

    <Container>
      <Row md={4} className="justify-content-md-center" style={{'marginTop': 60}}>
        <Col xs={6}>
          <Form onSubmit={handleSubmit(onSubmit)}>
            <Form.Group controlId="formUser">
              <Form.Label>Username</Form.Label>
              <Form.Control type="text" placeholder="Enter User" {...register("user")} />
            </Form.Group>

            <Form.Group controlId="formPassword" className={"mt-4"}>
              <Form.Label>Password</Form.Label>
              <Form.Control type="password" placeholder="Password" {...register("password")} />
            </Form.Group>

            <Button variant="primary" type="submit" className={"mt-5"}>
              Login
            </Button>
          </Form>
        </Col>
      </Row>
    </Container>
  );

};


const mapStateToProps = (state) => {
  return {
    isAuthenticated: !!state.token,
    isLoading: state.loading,
    error: state.error,
    is_staff: state.is_staff,
    is_superuser: state.is_superuser,
    is_active: state.is_active
  };
};

const mapDispatchToProps = dispatch => {
  return {
    onAuth: (username, password, enqueueSnackbar) => dispatch(actions.authLogin(username, password, enqueueSnackbar))
  };
};

export default connect(mapStateToProps, mapDispatchToProps)(LoginForm);

