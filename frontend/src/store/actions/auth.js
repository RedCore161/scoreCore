import axiosConfig from "../../axiosConfig";

import * as actionTypes from './actionTypes';
import { showErrorBar } from "../../components/ui/Snackbar";

const SESSION_EXPIRE = 3600;

export const authStart = () => {
  return {
    type: actionTypes.AUTH_START
  };
};

export const authSuccess = token => {
  return {
    type: actionTypes.AUTH_SUCCESS,
    token: token
  };
};

export const authFail = error => {
  return {
    type: actionTypes.AUTH_FAIL,
    error: error
  };
};

export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('expirationDate');
  return {
    type: actionTypes.AUTH_LOGOUT
  };
};

export const checkAuthTimeout = expirationTime => {
  return dispatch => {
    setTimeout(() => {
      dispatch(logout());
    }, expirationTime * 1000);
  };
};

export const authLogin = (username, password, enqueueSnackbar) => {

  return dispatch => {
    dispatch(authStart());
    axiosConfig.post('/rest-auth/login/', {
      username: username,
      password: password
    }, {
      timeout: 1000,
    })
      .then(res => {
        const token = res.data.key;
        const expirationDate = new Date(new Date().getTime() + SESSION_EXPIRE * 1000);
        localStorage.setItem('token', token);
        localStorage.setItem('expirationDate', expirationDate.getTime().toString());
        dispatch(authSuccess(token));
        dispatch(checkAuthTimeout(SESSION_EXPIRE));
      })
      .catch(err => {
        dispatch(authFail(err));
        console.log({err});
        console.error(err);
        showErrorBar(enqueueSnackbar, "Login failed!")
      });
  };
};

export const authCheckState = () => {
  return dispatch => {
    const token = localStorage.getItem('token');
    if (token === undefined) {
      dispatch(logout());
    } else {
      const expirationDate = new Date(parseInt(localStorage.getItem('expirationDate')));
      if (expirationDate <= new Date()) {
        dispatch(logout());
      } else {
        const expirationDate = new Date(new Date().getTime() + SESSION_EXPIRE * 1000);
        localStorage.setItem('expirationDate', expirationDate.getTime().toString());
        dispatch(authSuccess(token));
        dispatch(checkAuthTimeout(( expirationDate.getTime() - new Date().getTime() ) / 1000));
      }
    }
  };
};
