import { Routes, Route } from "react-router-dom";
import RootLayout from "./layouts/RootLayout";
import HomePage from "./pages/HomePage";
import ResumePage from "./pages/ResumePage";
import AgentStreamPage from "./pages/AgentStreamPage";
import SettingsPage from "./pages/SettingsPage.jsx";

function App() {
  return (
    <Routes>
      <Route path="/" element={<RootLayout />}>
        <Route index element={<HomePage />} />
        <Route path="resume" element={<ResumePage />} />
        <Route path="agents" element={<AgentStreamPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}

export default App;