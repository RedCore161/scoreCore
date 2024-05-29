import React from "react";
import axiosConfig from "./axiosConfig";
import ReactTimeAgo from "react-time-ago";

export const MULTISELECT_STYLE = {
  chips: {
    background: "green"
  },
  multiSelectContainer: {
    color: "red",
    background: "blue"
  },
  searchBox: {
    color: "yellow",
    background: "white",
    borderRadius: "var(--bs-border-radius)"
  },
  optionContainer: {
    color: "black",
    background: "white"
  }
};

export function getGradiColor(a, b) {
  // Ensure the value is within the range [0, 1]
  let value = b !== 0 ? a / b : 0
  if (value < 0) value = 0;
  if (value > 1) value = 1;

  // Calculate red and green components
  const red = Math.round(255 * (1 - value));
  const green = Math.round(255 * value);

  // Return the color in RGB format
  return `rgb(${red},${green},0)`;
}

export function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

export function range(start, end) {
  return Array.apply(0, Array(end)).map((element, index) => index + start);
}

export async function fetchProjects() {
  const result = await axiosConfig.holder.get("/api/project/list/");
  console.log("Found Projects:", result.data);
  return result.data
}

export async function fetchEvaluations() {
  const result = await axiosConfig.holder.get("/api/project/evaluations/");
  console.log("Found Evaluations:", result.data);
  return result.data
}

export async function fetchImage(id, params) {
  const url = params ? `/api/project/${ id }/image/?${ params }` :
                       `/api/project/${ id }/image/`
  const result = await axiosConfig.holder.get(url);
  console.log("Found Image:", result.data);
  return result.data
}

export async function fetchImagesAll(id, page=1) {
  const result = await axiosConfig.holder.get(`/api/project/${ id }/images/all?page=${page}`);
  console.log("Found All Images:", result.data);
  return result.data
}

export async function fetchFolders(setter) {
  await axiosConfig.holder.get(`/api/project/available/`).then((response) => {
    setter(response.data);
  }, (error) => {
    if (error.response) {
      console.error(error.response.data);
    } else {
      console.error(error);
    }
  });
}

export function updateOrAppend(elements, newData, field = "id") {
  if (elements !== undefined) {
    let index = elements.findIndex(element => element[field] === newData[field]);
    if (index === -1) {
      elements.push(newData);
      return elements;
    } else {
      elements[index] = newData;
    }
  }
  return elements;
}

export function updateOrPrepend(elements, newData, field = "id") {
  if (elements !== undefined) {
    let index = elements.findIndex(element => element[field] === newData[field]);
    if (index === -1) {
      elements.unshift(newData);
      return elements;
    } else {
      elements[index] = newData;
    }
  }
  return elements;
}

export function SelectListened({ options, onChange, disabled }) {
  return (
    <select className={ "form-select mb-3" } disabled={ disabled || null } onChange={ onChange }>
      { options.map(value => (
        <option key={ value } value={ value }>{ value }</option>
      )) }
    </select>
  );
}

export const columnScores = [
  {
    id: 1,
    name: "",
    sortable: true,
    width: "40px",
    cell: row => row.is_completed ? "✔" : "⭕",
    selector: row => row.is_completed,
  },
  {
    id: 2,
    name: "Filename",
    sortable: true,
    minwidth: "50px",
    maxwidth: "100px",
    cell: row => row.file_name,
    selector: row => row.file_name,
  },
  {
    id: 3,
    name: "Last Change",
    sortable: true,
    minwidth: "60px",
    cell: row => <ReactTimeAgo date={ row.timestamp } locale="en"/>,
    selector: row => row.timestamp,
  }
];

export const conditionalScoreRowStyles = [
  {
    when: row => row.date_end,
    style: {
      backgroundColor: "rgba(255,22,0,0.1)",
    },
  },
  {
    when: row => row.invoice_relevant,
    style: {
      backgroundColor: 'rgba(255, 255, 0, 0.1)',
    },
  },
  {
    when: row => row.ignore_export,
    style: {
      color: 'rgba(125, 125, 125, 0.5)',
    },
  },
];
