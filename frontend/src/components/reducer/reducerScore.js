import * as actionTypes from "./reducerTypes";

export const defaultStateScore = {
  "_comment": "",
  "_key": false,
  "_active": ""
};

export const reducerScore = (state, action) => {

  switch (action.type) {

    case actionTypes.SET_SCORE:
      let key = action.payload.action
      state[key] = action.payload.value
      return { ...state };

    case actionTypes.SET_COMMENT:
      return { ...state, _comment: action.payload};

    case actionTypes.SET_ACTIVE:
      return { ...state, _active: action.payload};

    case actionTypes.SET_INIT:
      return { ...state, ...action.payload};

    case actionTypes.SET_RESET:
      return defaultStateScore;

    default:
      throw new Error(`No matching action type: ${ action.type }`);
  }

};
