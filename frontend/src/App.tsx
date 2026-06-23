import { AuthProvider, useAuth } from './context/AuthContext';
import LoginScreen from './components/LoginScreen';
import SupportScreen from './components/SupportScreen';

function AppContent() {
  const { isLoggedIn } = useAuth();
  return isLoggedIn ? <SupportScreen /> : <LoginScreen />;
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
