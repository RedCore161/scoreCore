import ReactTimeAgo from "react-time-ago";
import React from "react";
import TimeAgo from "javascript-time-ago"
import de from "javascript-time-ago/locale/de"
import en from "javascript-time-ago/locale/en"
TimeAgo.addDefaultLocale(en)
TimeAgo.addLocale(de)

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
    maxwidth: "150px",
    cell: row => row.file_name,
    selector: row => row.file_name,
  },
  {
    id: 3,
    name: "Last Change",
    sortable: true,
    minwidth: "60px",
    cell: row => <ReactTimeAgo date={ row.timestamp } locale="en" />,
    selector: row => row.timestamp,
  }
];
