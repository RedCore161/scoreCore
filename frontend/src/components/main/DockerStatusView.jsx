import React, { useContext, useEffect, useState } from 'react';
import axiosConfig from "../../axiosConfig";
import DataTable from "react-data-table-component";
import ShowTextModal from "../modal/ShowTextModal";
import DockerActionButtons from "../ui/DockerActionButtons";
import {  Row } from "react-bootstrap";
import { CoreModalContext } from "../modal/coreModalContext";
import { WebSocketContext } from "../ws/websocketContext";

import "../ui/css/DockerStatusView.css"
import LoadingIcon from "../ui/LoadingIcon";
import { useAuthHeader } from "react-auth-kit";

const DockerStatusView = () => {

  const [status, setStatus] = useState({  });
  const [modalState, setModalState] = useContext(CoreModalContext)
  const { sendMessage, wsMessage } = useContext(WebSocketContext);
  const authHeader = useAuthHeader();

  useEffect(() => {
    console.log("useEffect")


    fetchDockerStatus();

  }, []);

  useEffect(() => {
    if (wsMessage) {
      let elements
      console.log("WS received =>", wsMessage);
      if (wsMessage.type === 'docker_status') {
        switch (wsMessage.event) {

          case 'updated':
            elements = status.container

            for (const [key, value] of Object.entries(wsMessage.data)) {
              let foundIndex = elements.findIndex(x => x.id === key);
              if (foundIndex > -1) {
                elements[foundIndex] = { "id": key, ...value }
              } else {
                elements.unshift({ "id": key, ...value })
              }
            }
            setStatus({...status, 'container': elements });
            break;

          case 'removed':
            elements = status.container
            wsMessage.data.forEach(doomed => {
              let foundIndex = elements.findIndex(x => x.id === doomed);
              if (foundIndex > -1) {
                elements.splice(foundIndex, 1)
              }
            })
            setStatus({...status, 'container': elements });
            break;
        }
      }
    }
  }, [wsMessage]);


  async function fetchDockerStatus() {
    axiosConfig.updateToken(authHeader());
    const result = await axiosConfig.holder.get("/api/docker/status");
    setStatus(result.data);
  }

  const columns = [
    {
      name: 'Container',
      sortable: true,
      cell: row => (<div style={ { paddingTop: '12px', paddingBottom: '12px' } }>
        <div className={ "dockerName" }>{ row["name"] }</div>{ row["id"] }
      </div>),
      selector: row => row.name,
    },
    {
      name: 'Status',
      width: '150px',
      sortable: true,
      selector: row => row.status,
    },
    {
      name: 'Actions',
      width: '300px',
      cell: row => <DockerActionButtons modalState={modalState} setModalState={setModalState} {  ...row } />,
    }
  ];

  const conditionalRowStyles = [
    {
      when: row => row.status === "running",
      style: {
        backgroundColor: 'rgba(63, 195, 128, 0.7)',
      },
    },
    {
      when: row => row.status === "exited",
      style: {
        backgroundColor: 'rgba(255,22,0,0.7)',
      },
    },
  ];

  const customStyles = {
    headCells: {
      style: {
        fontSize: '22px'
      },
    }
  };

  return (
    <>
      <ShowTextModal />

      { status.container ? (
        <DataTable
          title={ "Docker-Container Overview" }
          data={ status.container }
          columns={ columns }
          theme="dark"
          conditionalRowStyles={ conditionalRowStyles }
          customStyles={ customStyles }
        />
      ) : <Row><LoadingIcon /></Row> }
    </>
  );

}

export default DockerStatusView;
