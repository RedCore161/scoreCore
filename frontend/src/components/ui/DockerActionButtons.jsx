import React from 'react';
import { Button } from "react-bootstrap";
import { showErrorBar, showSuccessBar } from "./Snackbar";
import { useSnackbar } from "notistack";
import axiosConfig from "../../axiosConfig";

const DockerActionButtons = ({ modalState, setModalState, id, status }) => {

  const { enqueueSnackbar } = useSnackbar()

  function restartDockerContainer(id) {
    axiosConfig.post("api/docker/restart/", {
      container_id: id,
    }).then((response) => {
      if (response.data.success) {
        showSuccessBar(enqueueSnackbar, "Successfully restarted")
      } else {
        showErrorBar(enqueueSnackbar, "Restarting failed")
      }
    }, (error) => {
      if (error.response) {
        console.log(error.response.data);
      } else {
        console.error(error)
      }
    });
  }

  function removeDockerContainer(id) {
    axiosConfig.post("api/docker/remove/", {
      container_id: id,
    }).then((response) => {
      if (response.data.success) {
        showSuccessBar(enqueueSnackbar, "Successfully removed")
      } else {
        showErrorBar(enqueueSnackbar, "Removing failed")
      }
    }, (error) => {
      if (error.response) {
        console.log(error.response.data);
      } else {
        console.error(error)
      }
    });
  }

  function stopDockerContainer(id) {
    axiosConfig.post("api/docker/stop/", {
      container_id: id,
    }).then((response) => {
      if (response.data.success) {
        showSuccessBar(enqueueSnackbar, "Successfully stopped")
      } else {
        showErrorBar(enqueueSnackbar, "Stopping failed")
      }
    }, (error) => {
      if (error.response) {
        console.log(error.response.data);
      } else {
        console.error(error)
      }
    });
  }

  function showLogs(id) {
    axiosConfig.post("api/docker/logs/", {
      container_id: id,
    }).then((response) => {
      if (response.data.success) {
        setModalState({ ...modalState, modalShowText: true, title: response.data.name, txt: response.data.logs })
      } else {
        showErrorBar(enqueueSnackbar, "Could not get logs!")
      }
    }, (error) => {
      if (error.response) {
        console.log(error.response.data);
      } else {
        console.error(error)
      }
    });
  }

  return (
    <>
      <Button variant="danger" className={"me-1"} disabled={ status === "running"} onClick={ () => { removeDockerContainer(id)} } title={"Delete Container"}>
        <i className="bi bi-trash-fill"/>
      </Button>
      <Button variant="info" className={"me-1"} disabled={ status !== "running"} onClick={ () => { stopDockerContainer(id)} } title={"Stop Container"}>
        <i className="bi bi-pause-fill"/>
      </Button>
      <Button variant="info" className={"me-1"} onClick={ () => { restartDockerContainer(id)} } title={"Restart Container"}>
        <i className="bi bi-bootstrap-reboot" />
      </Button>
      <Button variant="info" className={"me-1"} onClick={ () => { showLogs(id)} } title={"See Logs"}>
        <i className="bi bi-book" />
      </Button>
    </>
  );
};

export default DockerActionButtons;
