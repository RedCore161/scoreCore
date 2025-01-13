import React, { useEffect, useState } from "react";
import { Button, Col, Row } from "react-bootstrap";
import BoxContainer from "../ui/BoxContainer";
import LoadingIcon from "../ui/LoadingIcon";
import axiosConfig from "../../axiosConfig";
import { showSuccessBar } from "../ui/Snackbar";
import { useSnackbar } from "notistack";
import CorePaginator from "../ui/CorePaginator";
import BackupButton from "../ui/BackupButton";

import { useAuth } from "../../../hooks/CoreAuthProvider";

const BackupView = () => {

  const [data, setData] = useState([]);
  const { enqueueSnackbar } = useSnackbar();
  const [urls, setUrls] = useState({ "backup": "/api/backup/?page=1" });
  const auth = useAuth();

  async function fetchBackups() {
    const result = await axiosConfig.perform_get(auth, urls.backup, (response) => {
      console.log("Found Backups:", response.data);
    });
    return result.data;
  }

  useEffect(() => {
    if ("backup" in urls) {
      fetchBackups().then((response) => {
        setData(response);
      });
    }
  }, [urls]);

  async function reloadBackup() {
    await axiosConfig.perform_post(auth, `/api/backup/reload/`, {},
      (response) => {
        setData(response.data);
        showSuccessBar(enqueueSnackbar, "Successfully reloaded Backups!");
      }, (error) => {
        if (error.response) {
          console.log(error.response.data);
        } else {
          console.error(error);
        }
      });
  }

  async function createBackup() {
    await axiosConfig.perform_post(auth, `/api/backup/create/`, {},
      (response) => {
        setData(response.data);
        showSuccessBar(enqueueSnackbar, "Successfully created Backup!");
      }, (error) => {
        if (error.response) {
          console.log(error.response.data);
        } else {
          console.error(error);
        }
      });
  }

  async function deleteAllBackups() {
    await axiosConfig.perform_post(auth, `/api/backup/deleteAll/`, {},
      (response) => {
        setData(response.data);
        showSuccessBar(enqueueSnackbar, "Successfully deleted all Backups!");
      }, (error) => {
        if (error.response) {
          console.log(error.response.data);
        } else {
          console.error(error);
        }
      });
  }

  async function deleteBackup(id) {
    await axiosConfig.perform_post(auth, `/api/backup/${ id }/delete/`, {},
      (response) => {
        setData(response.data);
        showSuccessBar(enqueueSnackbar, "Successfully deleted Backup!");
      }, (error) => {
        if (error.response) {
          console.log(error.response.data);
        } else {
          console.error(error);
        }
      });
  }

  async function restoreBackup(id, name) {
    await axiosConfig.perform_post(auth, `/api/backup/${ id }/restore/`, {},
      (response) => {
        setData(response.data);
        showSuccessBar(enqueueSnackbar, `Successfully restored "${ name }"!`);
      }, (error) => {
        if (error.response) {
          console.log(error.response.data);
        } else {
          console.error(error);
        }
      });
  }

  const handlePaginator = ({ selected }) => {
    setUrls({ ...urls, "backup": `/api/backup/?page=${ selected + 1 }` });
  };

  return (
    data ? (
      <>
        <BoxContainer title="Backup Actions">
          <Row>
            <Col>
              <Button className={ "btn-lg me-3" } variant={ "info" } onClick={ () => reloadBackup() }>
                Reload Backups</Button>
              <Button className={ "btn-lg me-3" } variant={ "success" } onClick={ () => createBackup() }>
                Create Backup</Button>
              <Button className={ "btn-lg" } variant={ "danger" } onClick={ () => deleteAllBackups() }>
                Delete All Backups</Button>
            </Col>
          </Row>
        </BoxContainer>

        <BoxContainer title="Available Backups">
          { "elements" in data && (
            <>
              { <CorePaginator pages={ data.pages }
                               handleChangePage={ handlePaginator }/> }

              { data.elements.map((backup) => {
                return <BackupButton key={ backup.id }
                                     callbackRestore={ restoreBackup } callbackDelete={ deleteBackup }
                                     { ...backup } />;

              }) }
            </>
          ) }

        </BoxContainer>
      </>
    ) : ( <Row><LoadingIcon/></Row> )
  );
};
export default BackupView;
