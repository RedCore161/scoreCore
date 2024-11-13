import React, { useEffect, useState } from "react";
import { Button, Col, Row } from "react-bootstrap";
import BoxContainer from "../ui/BoxContainer";
import LoadingIcon from "../ui/LoadingIcon";
import axiosConfig from "../../axiosConfig";
import { showSuccessBar } from "../ui/Snackbar";
import { useSnackbar } from "notistack";
import CorePaginator from "../ui/CorePaginator";
import BackupButton from "../ui/BackupButton";
import useAuthHeader from "react-auth-kit/hooks/useAuthHeader";

const BackupView = () => {

  const [data, setData] = useState([]);
  const { enqueueSnackbar } = useSnackbar();
  const [urls, setUrls] = useState({"backup": "/api/backup/?page=1"});
  const authHeader = useAuthHeader();

  async function fetchBackups() {
    axiosConfig.updateToken(authHeader());
    const result = await axiosConfig.holder.get(urls.backup);
    console.log("Found Backups:", result.data);
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
    axiosConfig.updateToken(authHeader());
    await axiosConfig.holder.post(`/api/backup/reload/`).then((response) => {
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
    axiosConfig.updateToken(authHeader());
    await axiosConfig.holder.post(`/api/backup/create/`).then((response) => {
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
    axiosConfig.updateToken(authHeader());
    await axiosConfig.holder.post(`/api/backup/deleteAll/`).then((response) => {
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
    axiosConfig.updateToken(authHeader());
    await axiosConfig.holder.post(`/api/backup/${id}/delete/`).then((response) => {
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
    axiosConfig.updateToken(authHeader());
    await axiosConfig.holder.post(`/api/backup/${ id }/restore/`).then((response) => {
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
    setUrls({...urls, "backup": `/api/backup/?page=${ selected + 1 }`});
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
                               handleChangePage={ handlePaginator } /> }

              { data.elements.map((backup) => {
                return <BackupButton key={backup.id}
                                     callbackRestore={restoreBackup} callbackDelete={deleteBackup}
                                     {...backup} />;

              }) }
            </>
          ) }

        </BoxContainer>
      </>
    ) : ( <Row><LoadingIcon/></Row> )
  );
};
export default BackupView;
