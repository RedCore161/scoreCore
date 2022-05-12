import React from 'react';

export function showSuccessBar(enqueueSnackbar, msg) {
  enqueueSnackbar(msg, { 'variant': 'success' });
}

export function showErrorBar(enqueueSnackbar, msg) {
  enqueueSnackbar(msg, { 'variant': 'error' });
}

export function showInfoBar(enqueueSnackbar, msg) {
  enqueueSnackbar(msg, { 'variant': 'info' });
}
