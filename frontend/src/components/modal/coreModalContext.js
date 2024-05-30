import React, { useState } from 'react';

const CoreModalContext = React.createContext([{}, p => {}]);

const ModalProvider = ({ children }) => {
  const [state, setState] = useState({});
  return (
    <CoreModalContext.Provider value={[state, setState]}>
      { children }
    </CoreModalContext.Provider>
  );
};
export { CoreModalContext, ModalProvider };
