import React from "react";
import { Container, Row } from "react-bootstrap";
import { SnackbarProvider } from "notistack";
import { BrowserRouter } from 'react-router';
import CoreAuthProvider from '../hooks/CoreAuthProvider';
import CoreRoutes from './CoreRoutes'
import { ModalProvider } from './components/modal/coreModalContext';


function App() {
  return (
    <SnackbarProvider maxSnack={5} anchorOrigin={{vertical: "top", horizontal: "right"}}
                      classes={ { anchorOriginTopRight: "customSnackbar" } }>
      <ModalProvider>
        <Container fluid={true} style={{minWidth: "550px"}}>
          <Row>
            <BrowserRouter>
              <CoreAuthProvider>
                <CoreRoutes />
              </CoreAuthProvider>
            </BrowserRouter>
          </Row>
        </Container>
      </ModalProvider>
    </SnackbarProvider>
  )
}
export default App;

