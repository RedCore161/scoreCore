export const getAcceptesTypes = (_type) => {
  switch (_type) {
    case "csv":
      return { "text/*": [".csv"], }
    case "video":
      return { "video/*": [".mp4", ".wepm"]}
    case "doc":
      return { "image/*": [], "application/pdf": [".pdf"], "text/*": [".csv"]}
    case "template":
      return {"application/*": [".odt", ".ods"]}
    default:
      return { "image/*": []}
  }
}
