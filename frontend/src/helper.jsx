import React from "react";
import axiosConfig from "./axiosConfig";

export function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

export function range(start, end) {
  return Array.apply(0, Array(end)).map((element, index) => index + start);
}

export async function fetchProjects(auth, setter) {
  await axiosConfig.perform_get(auth, "/api/project/list/",
    (response) => {
      setter(response.data);
      console.log("Found Projects:", response.data);
    });
}

export async function fetchEvaluations(auth) {
  const result = await axiosConfig.perform_get(auth, "/api/project/evaluations/", (response) => {
    console.log("Found Evaluations:", response.data);
  });
  return result.data;
}

export async function fetchImage(auth, id, params) {
  const url = params ? `/api/project/${ id }/image/?${ params }` :
    `/api/project/${ id }/image/`;
  const result = await axiosConfig.perform_get(auth, url, (response) => {
    console.log("Found Image:", response.data);
  });
  return result.data;
}

export async function fetchImagesAll(auth, id, page = 1) {
  const result = await axiosConfig.perform_get(auth, `/api/project/${ id }/images/all?page=${ page }`,
    (response) => {
      console.log("Found All Images:", response.data);
    });
  return result.data;
}

export async function fetchFolders(auth, setter) {
  await axiosConfig.perform_get(auth, `/api/project/available/`,
    (response) => {
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


export const conditionalScoreRowStyles = [
  {
    when: row => row.date_end,
    style: {
      backgroundColor: "rgba(255,22,0,0.1)",
    },
  }
];
