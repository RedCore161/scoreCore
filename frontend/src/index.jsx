import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "react-auth-kit"
import refreshApi from "./components/auth/refreshApi";
import App from "./App";
import "./style.scss";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <AuthProvider
    authName={ "_auth" }
    authType={ "cookie" }
    cookieDomain={ window.location.hostname }
    cookieSecure={ process.env.PROTOCOL === "https" }
    refresh={ refreshApi } >
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </AuthProvider>
);
