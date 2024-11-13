import axios from "axios";
import Cookies from "js-cookie";

export default class axiosConfig {
  static instance = null;
  axiosHolder = {};

  static get getInstance() {
    if (axiosConfig.instance == null) {
      axiosConfig.instance = new axiosConfig();
    }
    return this.instance;
  }

  static get holder() {
    return axiosConfig.getInstance.axiosHolder;
  }

  static updateToken(header) {
    if (header) {
      this.holder.defaults.headers.common["Authorization"] = `${ header }`;
    } else {
      console.error("Invalid JWT-Header")
    }
    return this.holder
  }

  constructor() {
    this.axiosHolder = axios.create({
      baseURL: process.env.REACT_APP_BACKEND_URL
    });

    let csrftoken = Cookies.get("csrftoken");

    if (csrftoken) {
      this.axiosHolder.defaults.headers.common["X-CSRFToken"] = `csrftoken ${ csrftoken }`;
    }

    // this.axiosHolder.defaults.headers.common['Cache-Control'] = `no-cache`;
    // this.axiosHolder.defaults.headers.common['Cross-Origin-Resource-Policy'] = `*`;

  }
}
