import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { LanguageProvider } from './i18n/LanguageContext';
import Landing from './pages/Landing';
import Test from './pages/Test';
import Results from './pages/Results';
import AdminLogin from './pages/admin/AdminLogin';
import AdminLayout from './pages/admin/AdminLayout';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminQuestions from './pages/admin/AdminQuestions';
import AdminIdols from './pages/admin/AdminIdols';
import AdminTraits from './pages/admin/AdminTraits';

function App() {
  return (
    <LanguageProvider>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Landing />} />
          <Route path="/test" element={<Test />} />
          <Route path="/results/:resultId" element={<Results />} />

          {/* Admin routes */}
          <Route path="/admin" element={<AdminLogin />} />
          <Route element={<AdminLayout />}>
            <Route path="/admin/dashboard" element={<AdminDashboard />} />
            <Route path="/admin/questions" element={<AdminQuestions />} />
            <Route path="/admin/idols" element={<AdminIdols />} />
            <Route path="/admin/traits" element={<AdminTraits />} />
          </Route>
        </Routes>
      </Router>
    </LanguageProvider>
  );
}

export default App;
