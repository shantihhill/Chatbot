import React from 'react';

import css from './App.module.css';
import Chat from '../Chat/Chat';
import logo from '../../assets/velogowhite.png';

function App() {

  return (
    <div className={css['app-window']}>
      <header className={css['header']}>
        <img src={logo} style={{height: '60px', width: 'auto'}}></img>
      </header>
      <div className={css['chat-window']}>
        <Chat />
      </div>
    </div>
  );
}

export default App;