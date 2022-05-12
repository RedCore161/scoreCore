import axios from 'axios';
import Cookies from "js-cookie";

const instance = axios.create({
  baseURL: process.env.REACT_APP_BACKEND_URL
});

let token = localStorage.getItem("token");
if (token) {
  instance.defaults.headers.common['Authorization'] = `token ${ token }`;
}

let csrftoken = Cookies.get('csrftoken');
if (csrftoken) {
  instance.defaults.headers.common['X-CSRFToken'] = `csrftoken ${ csrftoken }`;
}

instance.defaults.headers.common["Access-Control-Allow-Origin"] = process.env.REACT_APP_BACKEND_RAW_URL
instance.defaults.headers.common["Access-Control-Allow-Headers"] = "*"

export default instance;
