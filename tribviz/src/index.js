import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import { createStore, combineReducers } from 'redux'
import { Provider } from 'react-redux'

import frameReducer from './reducers/frameReducer'
import setupReducer from './reducers/setupReducer';

const reducer = combineReducers({
  frames: frameReducer,
  setup: setupReducer
})

const store = createStore(reducer)


ReactDOM.render(
  <Provider store={store}>

    <App />

  </Provider>,
  document.getElementById('root')
);
