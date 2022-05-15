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

  refreshData() {
    const holder = axiosConfig.getInstance.axiosHolder
    let token = localStorage.getItem("token");
    if (token) {
      holder.defaults.headers.common['Authorization'] = `token ${ token }`;
    }

    let csrftoken = Cookies.get('csrftoken');
    if (csrftoken) {
      holder.defaults.headers.common['X-CSRFToken'] = `csrftoken ${ csrftoken }`;
    }

  }

  constructor() {
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
