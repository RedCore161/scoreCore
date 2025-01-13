import axios, {AxiosError, AxiosInstance} from "axios";
import Cookies from "js-cookie";
import {AuthContextType} from "../hooks/CoreAuthProvider";

export default class axiosConfig {
  static instance;
  axiosHolder: AxiosInstance;

  constructor() {
    this.axiosHolder = axios.create({
      baseURL: process.env.REACT_APP_BACKEND_URL,
    });

    const csrftoken = Cookies.get('csrftoken');

    if (csrftoken) {
      this.axiosHolder.defaults.headers.common['X-CSRFToken'] =
        `csrftoken ${csrftoken}`;
    }

    // this.axiosHolder.defaults.headers.common['Cache-Control'] = `no-cache`;
    // this.axiosHolder.defaults.headers.common['Cross-Origin-Resource-Policy'] = `*`;
  }

  static get getInstance() {
    if (axiosConfig.instance == null) {
      axiosConfig.instance = new axiosConfig();
    }
    return this.instance;
  }

  static get holder() {
    return axiosConfig.getInstance.axiosHolder;
  }

  static async perform_post(
    auth: AuthContextType | undefined,
    url: string,
    data,
    callBackSuccess,
    callBackError = (error) => {
      if (error.response) {
        console.log(error.response.data);
      } else {
        console.error(error);
      }
    },
    config,
  ) {
    axiosConfig.updateToken(config?.token);
    await axiosConfig.holder.post(url, data, config).then(
      (response) => {
        callBackSuccess(response);
      },
      (error) => {
        if (error.response.status === 401) {
          if (auth?.token) {
            auth.navigate(`/login?forward=${auth.location}`);
            return;
          }
        }
        callBackError(error);
      },
    );
  }

  static async perform_get(
    auth: AuthContextType,
    url,
    callBackSuccess = (response) => {},
    callBackError = (error: AxiosError) => {
      if (error.response) {
        console.log(error.response.data);
      } else {
        console.error(error);
      }
    },
    config = {},
  ) {
    axiosConfig.updateToken();
    await axiosConfig.holder.get(url, config).then(
      (response) => callBackSuccess(response)
    ) .catch(function (error) {
      if (error.response) {
        callBackError(error);
        if (error.response.status === 401) {
          auth?.navigate(`/login?forward=${auth.location}`);
          return;
        }
      } else if (error.request) {
        // The request was made but no response was received
        // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
        // http.ClientRequest in node.js
        console.log(error.request);
      } else {
        // Something happened in setting up the request that triggered an Error
        console.log('Error', error.message);
      }
      console.log(error.config);
    });
  }

  static updateToken(token = undefined) {
    if (token) {
      axiosConfig.holder.defaults.headers.common['Authorization'] =
        `Token ${token}`;
    } else {
      const authToken = localStorage.getItem('authToken');
      if (authToken) {
        axiosConfig.holder.defaults.headers.common['Authorization'] =
          `Bearer ${authToken}`;
      }
    }
    return axiosConfig.holder;
  }
}
