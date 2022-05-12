const path = require('path');
const webpack = require('webpack');

module.exports = {
  devtool: 'inline-source-map',
  entry: ['./client/src/index.js'],
  output: {
    path: path.join(__dirname, 'client', 'build'),
    filename: 'bundle.js'
  }
};
