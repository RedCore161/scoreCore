import React from "react";
import { Container, Row } from "react-bootstrap";
import { SnackbarProvider } from "notistack";
import { ModalProvider } from "./components/modal/coreModalContext";
import CoreRoutes from "./CoreRoutes"
import {BrowserRouter} from "react-router-dom";
import AuthProvider from "react-auth-kit";
import createStore from "react-auth-kit/createStore";

import refreshApi from "./components/auth/refreshApi";
import ReactRouterPlugin from '@auth-kit/react-router/route'

const store = createStore({
  authName: "_auth",
  authType: "cookie",
  cookieDomain: window.location.hostname,
  cookieSecure: window.location.protocol === 'https:',
  refresh: refreshApi,
  debug: process.env.DEBUG == "true" || false
});



function App() {
  return (
    <SnackbarProvider maxSnack={5} anchorOrigin={{vertical: "top", horizontal: "right"}}
                      classes={ { anchorOriginTopRight: "customSnackbar" } }>
      <ModalProvider>
        <Container fluid={true} style={{minWidth: "550px"}}>
          <Row>
            <BrowserRouter>
              <AuthProvider store={store} router={ReactRouterPlugin} fallbackPath="/login">
                <CoreRoutes />
              </AuthProvider>
            </BrowserRouter>
          </Row>
        </Container>
      </ModalProvider>
    </SnackbarProvider>
  )
}
export default App;

