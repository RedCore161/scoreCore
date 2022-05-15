import React from "react";
import axiosConfig from "./axiosConfig";

export async function fetchProjects() {
  const result = await axiosConfig.holder.get("/api/project/list/");
  console.log("Found Projects:", result.data);
  return result.data
}

export async function fetchImages(id) {
  const result = await axiosConfig.holder.get(`/api/project/${ id }/images/`);
  console.log("Found Images:", result.data);
  return result.data
}

export async function fetchBackups() {
  const result = await axiosConfig.holder.get(`/api/backup/`);
  console.log("Found Backups:", result.data);
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
