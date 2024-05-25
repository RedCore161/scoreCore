export const configIntegerNeeded = {
  required: {
    value: true,
    message: "This field is required!"
  },
  pattern: {
    value: /^[+-]?[0-9]*([.,][0-9]{0,3})?$/i,
    message: "Not valid!"
  }
}

export const configInteger = {
  required: false,
  pattern: {
    value: /^[+-]?([0-9]*[.,])?[0-9]{0,3}$/i,
    message: "Not valid!"
  }
}

export const configTextNeeded = {
  required: {
    value: true,
    message: "This field is required!"
  },
  minLength: {
    value: 2,
    message: "Too short",
  }
}

export const configText = {
  minLength: {
    value: 2,
    message: "Too short",
  }
}

export const configMail = {
  required: false,
  pattern: {
    value: /\S+@\S+\.\S+/,
    message: "No valid E-Mail",
  }
}

export const configCashBooking = {
  required: {
    value: true,
    message: "This field is required!"
  },
  pattern: {
    value: /^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[012])\.((20)?\d{2});[\-\w\d_äöüÄÖÜß&(),#+ ]+;[\-\w\d_äöüÄÖÜß&(),#+ ]+;[+-]?[0-9]+([.,][0-9]{0,2})?$/gm,
    message: "No valid Cash-Line",
  }
}
