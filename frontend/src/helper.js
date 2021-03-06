import React from "react";
import axiosConfig from "./axiosConfig";

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

export async function fetchImage(id) {
  const result = await axiosConfig.holder.get(`/api/project/${ id }/image/`);
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
