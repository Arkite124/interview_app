import { Routes, Route, Navigate } from "react-router-dom";
import RootLayout from "./layouts/RootLayout";
import HomePage from "./pages/HomePage";
import ResumePage from "./pages/ResumePage";
import AgentStreamPage from "./pages/AgentStreamPage";
import SettingsPage from "./pages/SettingsPage.jsx";
import QaLayout from "./layouts/QaLayout";
import RagPage from "./pages/qa/RagPage";
import ChatPage from "./pages/qa/ChatPage";
import StructuredPage from "./pages/qa/StructuredPage";
import ParallelPage from "./pages/qa/ParallelPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<RootLayout />}>
        <Route index element={<HomePage />} />
        <Route path="resume" element={<ResumePage />} />
        <Route path="agents" element={<AgentStreamPage />} />
        <Route path="qa" element={<QaLayout />}>
          <Route index element={<Navigate to="rag" replace />} />
          <Route path="rag" element={<RagPage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="structured" element={<StructuredPage />} />
          <Route path="parallel" element={<ParallelPage />} />
        </Route>
        <Route path="settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}

export default App;