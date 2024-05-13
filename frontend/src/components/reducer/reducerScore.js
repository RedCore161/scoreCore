import * as actionTypes from "./reducerTypes";

export const defaultStateScore = {
  "eye": "",
  "nose": "",
  "cheek": "",
  "ear": "",
  "whiskers": "",
  "comment": "",

  "key": false,

  "active": "eye"
};

export const reducerScore = (state, action) => {

  switch (action.type) {

    case actionTypes.SET_SCORE:
      switch (action.payload.action) {
        case "eye": return { ...state, eye: action.payload.value, active: "nose" };
        case "nose": return { ...state, nose: action.payload.value, active: "cheek" };
        case "cheek": return { ...state, cheek: action.payload.value, active: "ear" };
        case "ear": return { ...state, ear: action.payload.value, active: "whiskers" };
        case "whiskers": return { ...state, whiskers: action.payload.value, active: "" };
        default: return { ...state, active: ""};
      }

    case actionTypes.SET_COMMENT:
      return { ...state, comment: action.payload};

    case actionTypes.SET_ACTIVE:
      return { ...state, active: action.payload};

    case actionTypes.SET_RESET:
      return defaultStateScore;

    default:
      throw new Error(`No matching action type: ${ action.type }`);
  }

};
