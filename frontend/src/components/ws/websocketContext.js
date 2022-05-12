import React, { useCallback, useEffect, useRef } from 'react';
import useWebSocket from "react-use-websocket";

const WebSocketContext = React.createContext([{}, p => {}]);

const WebSocketProvider = ({ children, url }) => {

    const getSocketUrl = useCallback(() => {
      const ws_url = process.env.REACT_APP_BASE_WS+url;
      return new Promise(resolve => {
        setTimeout(() => {
          resolve(ws_url);
        }, 2000);
      });
    }, []);

    const didUnmount = useRef(false);
    const { sendMessage, lastMessage, readyState } = useWebSocket(getSocketUrl, {
        shouldReconnect: () => {
          return didUnmount.current === false;
        },
        reconnectAttempts: 3,
        reconnectInterval: 3000,
      }
    );

    useEffect(() => {
      return () => {
        didUnmount.current = true;
      };
    }, []);

    const wsMessage = lastMessage !== null ? JSON.parse(lastMessage.data) : null;

    return (
      <>
        <WebSocketContext.Provider value={ { sendMessage, wsMessage, readyState } }>
          { children }
        </WebSocketContext.Provider>
      </>
    );
  }
;

export { WebSocketContext, WebSocketProvider };
