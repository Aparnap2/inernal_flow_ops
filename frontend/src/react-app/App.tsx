import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from '../components/Layout';
import Dashboard from '../pages/Dashboard';
import AGUIPage from '../pages/AGUIPage';
import ApprovalsPage from '../pages/ApprovalsPage';
import ExceptionsPage from '../pages/ExceptionsPage';
import RunsPage from '../pages/RunsPage';
import AccountsPage from '../pages/AccountsPage';
import ContactsPage from '../pages/ContactsPage';
import SettingsPage from '../pages/SettingsPage';
import LoginPage from '../pages/LoginPage';
import RegisterPage from '../pages/RegisterPage';
import UnauthorizedPage from '../pages/UnauthorizedPage';
import ProtectedRoute from '../components/ProtectedRoute';
import { CopilotKit } from '@copilotkit/react-core';
import { AppProvider } from '../contexts/AppContext';
import { AuthProvider } from '../contexts/AuthContext';
import ErrorBoundary from '../components/ErrorBoundary';
import { setupErrorHandling } from '../utils/logger';

// Set up global error handling
setupErrorHandling();

function App() {
  return (
    <AuthProvider>
      <CopilotKit runtimeUrl="/copilotkit">
        <AppProvider>
          <Router>
            <ErrorBoundary>
              <Routes>
                {/* Public routes */}
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/unauthorized" element={<UnauthorizedPage />} />
                
                {/* Protected routes */}
                <Route path="/" element={
                  <ProtectedRoute>
                    <Layout>
                      <Dashboard />
                    </Layout>
                  </ProtectedRoute>
                } />
                <Route path="/dashboard" element={
                  <ProtectedRoute>
                    <Layout>
                      <Dashboard />
                    </Layout>
                  </ProtectedRoute>
                } />
                <Route path="/agui" element={
                  <ProtectedRoute>
                    <Layout>
                      <AGUIPage />
                    </Layout>
                  </ProtectedRoute>
                } />
                <Route path="/runs" element={
                  <ProtectedRoute>
                    <Layout>
                      <RunsPage />
                    </Layout>
                  </ProtectedRoute>
                } />
                <Route path="/approvals" element={
                  <ProtectedRoute requiredRole="OPERATOR">
                    <Layout>
                      <ApprovalsPage />
                    </Layout>
                  </ProtectedRoute>
                } />
                <Route path="/exceptions" element={
                  <ProtectedRoute requiredRole="OPERATOR">
                    <Layout>
                      <ExceptionsPage />
                    </Layout>
                  </ProtectedRoute>
                } />
                <Route path="/accounts" element={
                  <ProtectedRoute>
                    <Layout>
                      <AccountsPage />
                    </Layout>
                  </ProtectedRoute>
                } />
                <Route path="/contacts" element={
                  <ProtectedRoute>
                    <Layout>
                      <ContactsPage />
                    </Layout>
                  </ProtectedRoute>
                } />
                <Route path="/settings" element={
                  <ProtectedRoute requiredRole="ADMIN">
                    <Layout>
                      <SettingsPage />
                    </Layout>
                  </ProtectedRoute>
                } />
                <Route path="/admin/users" element={
                  <ProtectedRoute requiredRole="ADMIN">
                    <Layout>
                      <SettingsPage />
                    </Layout>
                  </ProtectedRoute>
                } />
                
                {/* Catch-all redirect to dashboard for authenticated users */}
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </ErrorBoundary>
          </Router>
        </AppProvider>
      </CopilotKit>
    </AuthProvider>
  );
}

export default App;
