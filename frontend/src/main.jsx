import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import { ActorProvider } from './context/ActorContext.jsx';
import './styles.css';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ActorProvider>
      <App />
    </ActorProvider>
  </StrictMode>,
);