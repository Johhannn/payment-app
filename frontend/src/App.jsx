import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import PaymentPage from './pages/PaymentPage';
import EMISchedulePage from './pages/EMISchedulePage';
import UserPage from './pages/UserPage';
import HeroSection from './components/HeroSection';
import LoginPage from './pages/LoginPage';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<HeroSection />} />

          <Route path="/payment" element={
            <ProtectedRoute>
              <PaymentPage />
            </ProtectedRoute>
          } />

          <Route path="/emi" element={
            <ProtectedRoute>
              <EMISchedulePage />
            </ProtectedRoute>
          } />

          <Route path="/users" element={
            <ProtectedRoute adminOnly={true}>
              <UserPage />
            </ProtectedRoute>
          } />

          <Route path="/rules" element={<div className="text-center mt-20 text-slate-500">Rules Management (Coming Soon)</div>} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
