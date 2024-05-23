import React from "react";
import axiosConfig from "./axiosConfig";
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

export function SelectListened({ options, onChange, disabled }) {
  return (
    <select className={ "form-select mb-3" } disabled={ disabled || null } onChange={ onChange }>
      { options.map(value => (
        <option key={ value } value={ value }>{ value }</option>
      )) }
    </select>
  );
}
