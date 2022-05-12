import React from "react";

export function pretty_amount(amount, hideZero=false) {

  if (amount > 0) {
    return <span style={ { color: "green" } }>{ amount.toLocaleString('de', { minimumFractionDigits: 2 }) }&euro;</span>;
  } else if (amount < 0) {
    return <span style={ { color: "red" } }>{ amount.toLocaleString('de', { minimumFractionDigits: 2 }) }&euro;</span>;
  }

  if (hideZero) {
    return <>&nbsp;</>;
  }

  return <>0,00 &euro;</>;
}


// https://jbetancur.github.io/react-data-table-component/?path=/story/conditional-styling--conditional-rows
export const columns50 = [
  {
    name: "Date",
    selector: "date",
    sortable: true,
    width: "110px"
  },
  {
    name: 'Recipient',
    selector: "recipient",
    sortable: true,
    width: "200px"
  },
  {
    name: 'Reference',
    selector: "reference",
    sortable: true,
    width: "225px"
  },
  {
    name: 'Amount',
    right: true,
    selector: "amount",
    sortable: true,
    width: "110px",
    cell: row => (
      <div>{ pretty_amount(row.amount) }</div>
    ),
  }
];


export function SelectListened({ options, onChange, disabled, selected }) {
  return (
    <select className={ "form-select mb-3" } disabled={ disabled || null } onChange={ onChange }>
      { Object.entries(options).map(([key, value]) => {
        return <option key={ value } value={ key } selected={selected === key}>{ value }</option>
      })}
    </select>
  );
}
