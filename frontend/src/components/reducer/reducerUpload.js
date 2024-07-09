import * as actionTypes from "./reducerTypes";

export const defaultStateUpload = {
  counter: 0,
  chunks: 0,
  uploading: false,
  error: "",
};

export const reducerUpload = (state, action) => {

  switch (action.type) {

    case actionTypes.START_UPLOADS:
      return { ...state, chunks: action.payload, uploading: true};

    case actionTypes.FINISH_UPLOAD:
      let new_counter = state.counter + 1
      return { ...state, counter: new_counter, uploading: new_counter < state.chunks };

    case actionTypes.FAILED_UPLOAD:
      return { ...state, error: action.payload, uploading: false};

    case actionTypes.SET_RESET:
      return defaultStateUpload;

    default:
      throw new Error(`No matching action type: ${ action.type }`);
  }

};
