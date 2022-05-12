import React, { useState } from 'react';
import ReactCrop from 'react-image-crop';
import 'react-image-crop/dist/ReactCrop.css';

const ImageCropper = ({ onChanges, init }) => {

  const [state, setState] = useState({
    crop: { ...init, unit: '%' } || {
      unit: '%',
      width: 80,
      height: 80,
      x: 10,
      y: 10
    },
  });

  const onCropChange = (crop, percentCrop) => {
    setState({ crop: percentCrop });
    onChanges({ ...percentCrop });
  };

  return (
    <ReactCrop
      src="/assets/immer-bereit.jpeg"
      crop={ state.crop }
      ruleOfThirds
      onChange={ onCropChange }
    />
  );

};

export default ImageCropper;
