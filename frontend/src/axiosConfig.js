import axios from 'axios';
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
  static get refreshData() {
    axiosConfig.instance = new axiosConfig();
    return axiosConfig.getInstance.axiosHolder;
  }

  constructor() {
    console.log("Construct axiosHolder")
    this.axiosHolder = axios.create({
      baseURL: process.env.REACT_APP_BACKEND_URL
    });
    let token = localStorage.getItem("token");
    if (token) {
      this.axiosHolder.defaults.headers.common['Authorization'] = `token ${ token }`;
    }

    let csrftoken = Cookies.get('csrftoken');
    if (csrftoken) {
      this.axiosHolder.defaults.headers.common['X-CSRFToken'] = `csrftoken ${ csrftoken }`;
    }
  }
}
