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
