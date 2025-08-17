import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import "./App.css";

// Components
import Header from "./components/common/Header";
import Sidebar from "./components/common/Sidebar";
import Dashboard from "./components/dashboard/Dashboard";
import TransactionList from "./components/transactions/TransactionList";
import TransactionDetail from "./components/transactions/TransactionDetail";
import ExplanationView from "./components/explanations/ExplanationView";
import ModelRegistry from "./components/models/ModelRegistry";
import DriftMonitor from "./components/drift/DriftMonitor";
import AlertManager from "./components/alerts/AlertManager";
import LoadingSpinner from "./components/common/LoadingSpinner";

// Hooks and Services
import { useAuth } from "./hooks/useAuth";
import { useWebSocket } from "./hooks/useWebSocket";

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { isAuthenticated, isLoading, login, logout } = useAuth();
  const { isConnected, lastMessage } = useWebSocket(
    process.env.REACT_APP_WS_URL || "ws://localhost:8080/ws"
  );

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md w-96">
          <h1 className="text-2xl font-bold text-center mb-6">
            Fraud Detection System
          </h1>
          <button
            onClick={login}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
          >
            Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Header
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          onLogout={logout}
          wsConnected={isConnected}
        />

        <div className="flex">
          <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

          <main
            className={`flex-1 transition-all duration-300 ${
              sidebarOpen ? "ml-64" : "ml-0"
            }`}
          >
            <div className="p-6">
              <Routes>
                <Route
                  path="/"
                  element={<Navigate to="/dashboard" replace />}
                />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/transactions" element={<TransactionList />} />
                <Route
                  path="/transactions/:id"
                  element={<TransactionDetail />}
                />
                <Route path="/explanations/:id" element={<ExplanationView />} />
                <Route path="/models" element={<ModelRegistry />} />
                <Route path="/drift" element={<DriftMonitor />} />
                <Route path="/alerts" element={<AlertManager />} />
              </Routes>
            </div>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
