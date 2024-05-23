import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "react-auth-kit"
import refreshApi from "./components/auth/refreshApi";
import App from "./App";
import TimeAgo from 'javascript-time-ago'
import de from 'javascript-time-ago/locale/de'
import en from 'javascript-time-ago/locale/en'
import "./style.scss";

TimeAgo.addDefaultLocale(en)

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
// reportWebVitals();
