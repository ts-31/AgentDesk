import { useState } from 'react';
import LoginScreen from './components/LoginScreen';
import SupportScreen from './components/SupportScreen';

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  return (
    <>
      {isLoggedIn ? (
        <SupportScreen />
      ) : (
        <LoginScreen onLogin={() => setIsLoggedIn(true)} />
      )}
    </>
  );
}
