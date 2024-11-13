import React from "react"
import ReactDOM from "react-dom/client"
import App from "./App";
import "./style.scss";

const app = process.env.DEBUG ? <React.StrictMode><App /></React.StrictMode> : <App />
ReactDOM.createRoot(document.getElementById("root")).render(app)


