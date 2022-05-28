import axiosConfig from "../../axiosConfig";

import * as actionTypes from './actionTypes';
import { showErrorBar } from "../../components/ui/Snackbar";

const SESSION_EXPIRE = 3600;

export const authStart = () => {
  return {
    type: actionTypes.AUTH_START
  };
};

export const authSuccess = ({key, is_staff=false, is_superuser=false, is_active=false}) => {
  return {
    type: actionTypes.AUTH_SUCCESS,
    token: key,
    is_staff: is_staff || false,
    is_superuser: is_superuser || false,
    is_active: is_active || false,
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
    // TODO fix later
    // setTimeout(() => {
    //   dispatch(logout());
    // }, expirationTime * 1000);
  };
};

export const authLogin = (username, password, enqueueSnackbar) => {

  return dispatch => {
    dispatch(authStart());
    axiosConfig.holder.post('/rest-auth/login/', {
      username: username,
      password: password
    }, {
      timeout: 1000,
    })
      .then(res => {
        const expirationDate = new Date(new Date().getTime() + SESSION_EXPIRE * 1000);
        localStorage.setItem("is_staff", res.data.is_staff);
        localStorage.setItem("is_superuser", res.data.is_superuser);
        localStorage.setItem("is_active", res.data.is_active);
        localStorage.setItem("token", res.data.key);
        localStorage.setItem("expirationDate", expirationDate.getTime().toString());
        dispatch(authSuccess(res.data));
        dispatch(checkAuthTimeout(SESSION_EXPIRE));
      })
      .catch(err => {
        dispatch(authFail(err));
        console.log({ err });
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
        dispatch(authSuccess({"key": token,
                                                       "is_staff": localStorage.getItem('is_staff'),
                                                       "is_superuser": localStorage.getItem('is_superuser'),
                                                       "is_active": localStorage.getItem('is_active')
        }));
        dispatch(checkAuthTimeout(( expirationDate.getTime() - new Date().getTime() ) / 1000));
      }
    }
  };
};
