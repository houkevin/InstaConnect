import React from 'react';
import ReactDOM from 'react-dom';

import App from './app';

// This method is only called once
ReactDOM.render(<App url="/api/v1/" />, document.getElementById('reactEntry'));
