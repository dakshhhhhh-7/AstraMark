import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { AuthProvider } from '@/contexts/AuthContext';
import { Toaster } from '@/components/ui/sonner';
import { queryClient } from '@/lib/react-query';
import ErrorBoundary from './ErrorBoundary';
import '@/App.css';

// Lazy load pages for code splitting
import { lazy, Suspense } from 'react';
import { LoadingOverlay } from '@/components/ui/loading-spinner';
import { ProtectedRoute } from '@/components/ProtectedRoute';

// Public pages
const LandingPage = lazy(() => import('@/pages/LandingPage'));
const LoginPage = lazy(() => import('@/pages/LoginPage'));
const RegisterPage = lazy(() => import('@/pages/RegisterPage'));
const PricingPage = lazy(() => import('@/pages/PricingPage'));

// Protected pages
const Dashboard = lazy(() => import('@/pages/Dashboard'));
const OnboardingPage = lazy(() => import('@/pages/OnboardingPage'));
const SettingsPage = lazy(() => import('@/pages/SettingsPage'));

// Test page (development only)
const TestPage = lazy(() => import('@/pages/TestPage'));

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Router>
          <AuthProvider>
            <Toaster position="top-right" richColors />
            <Suspense fallback={<LoadingOverlay message="Loading..." />}>
              <Routes>
                {/* Public routes */}
                <Route path="/" element={<LandingPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/pricing" element={<PricingPage />} />
                
                {/* Test page - development only */}
                {process.env.NODE_ENV === 'development' && (
                  <Route path="/test" element={<TestPage />} />
                )}

                {/* Protected routes */}
                <Route element={<ProtectedRoute />}>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/onboarding" element={<OnboardingPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                </Route>

                {/* Fallback - redirect to landing page */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Suspense>
          </AuthProvider>
        </Router>
        {/* React Query DevTools - only in development */}
        {process.env.NODE_ENV === 'development' && (
          <ReactQueryDevtools initialIsOpen={false} />
        )}
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
