import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { AppProvider } from './contexts/AppContext';
import { CopilotKit } from '@copilotkit/react-core';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import AGUIPage from './pages/AGUIPage';
import ApprovalsPage from './pages/ApprovalsPage';
import ExceptionsPage from './pages/ExceptionsPage';
import RunsPage from './pages/RunsPage';
import AccountsPage from './pages/AccountsPage';
import ContactsPage from './pages/ContactsPage';
import SettingsPage from './pages/SettingsPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import UnauthorizedPage from './pages/UnauthorizedPage';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <CopilotKit runtimeUrl="/copilotkit">
        <AuthProvider>
          <AppProvider>
            <Router>
              <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/unauthorized" element={<UnauthorizedPage />} />
                <Route path="/*" element={
                  <ProtectedRoute>
                    <Layout>
                      <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/agui" element={<AGUIPage />} />
                        <Route path="/approvals" element={<ApprovalsPage />} />
                        <Route path="/exceptions" element={<ExceptionsPage />} />
                        <Route path="/runs" element={<RunsPage />} />
                        <Route path="/accounts" element={<AccountsPage />} />
                        <Route path="/contacts" element={<ContactsPage />} />
                        <Route path="/settings" element={<SettingsPage />} />
                      </Routes>
                    </Layout>
                  </ProtectedRoute>
                } />
              </Routes>
            </Router>
          </AppProvider>
        </AuthProvider>
      </CopilotKit>
    </ErrorBoundary>
  );
}

export default App;
