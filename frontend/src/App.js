import React from 'react';
import { Container, Row } from "react-bootstrap";
import { SnackbarProvider } from "notistack";
import { ModalProvider } from "./components/modal/coreModalContext";
import MainContent from "./components/ui/MainContent";

const App = () => {

  return (
    <SnackbarProvider maxSnack={ 5 } anchorOrigin={ { vertical: "top", horizontal: "right" } }
                      classes={ { anchorOriginTopRight: "customSnackbar" } }>
      <ModalProvider>
        <Container fluid >
          <Row>
            <MainContent />
          </Row>
        </Container>
      </ModalProvider>
    </SnackbarProvider>
  );
}
export default App;
