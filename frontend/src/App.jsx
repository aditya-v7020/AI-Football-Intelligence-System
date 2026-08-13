import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ErrorBoundary from './components/common/ErrorBoundary';
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import PlayerSearch from './pages/PlayerSearch';
import PlayerComparison from './pages/PlayerComparison';
import Scout from './pages/Scout';
import Settings from './pages/Settings';

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/players" element={<PlayerSearch />} />
            <Route path="/compare" element={<PlayerComparison />} />
            <Route path="/scout" element={<Scout />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
