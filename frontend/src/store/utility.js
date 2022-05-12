import {useState} from "react";

export const updateObject = (oldObject, updatedProperties) => {
    return { ...oldObject, ...updatedProperties };
};

export function UseForceUpdate() {
    const [value, setValue] = useState(false);
    return () => setValue(true);
}
