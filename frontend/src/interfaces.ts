interface MultiselectButtonInterface {
  name: string,
  targetField: string,
  operator: "is" | "startsWith" | "endsWith" | "contains";
  variant: "button" | "checkbox";
  soloSelection: boolean;
  width: number;
}
