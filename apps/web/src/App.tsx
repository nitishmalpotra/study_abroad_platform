import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ModalProvider } from './context/ModalContext';
import Layout from './components/layout/Layout';
import HomePage from './pages/HomePage';
import DestinationsPage from './pages/DestinationsPage';
import CountryDetailPage from './pages/CountryDetailPage';
import UniversitiesPage from './pages/UniversitiesPage';
import ToolsPage from './pages/ToolsPage';
import EMICalculatorPage from './pages/EMICalculatorPage';
import SOPReviewPage from './pages/SOPReviewPage';
import ResourcesPage from './pages/ResourcesPage';
import BlogPage from './pages/BlogPage';
import BlogPostPage from './pages/BlogPostPage';

export default function App() {
  return (
    <BrowserRouter>
      <ModalProvider>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/destinations" element={<DestinationsPage />} />
            <Route path="/destinations/:id" element={<CountryDetailPage />} />
            <Route path="/universities" element={<UniversitiesPage />} />
            <Route path="/tools" element={<ToolsPage />} />
            <Route path="/tools/emi-calculator" element={<EMICalculatorPage />} />
            <Route path="/tools/sop-review" element={<SOPReviewPage />} />
            <Route path="/tools/resources" element={<ResourcesPage />} />
            <Route path="/blog" element={<BlogPage />} />
            <Route path="/blog/:id" element={<BlogPostPage />} />
          </Route>
        </Routes>
      </ModalProvider>
    </BrowserRouter>
  );
}
