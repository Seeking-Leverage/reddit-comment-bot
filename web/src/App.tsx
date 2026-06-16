import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import BrandPage from "./pages/Brand";
import GeneratorPage from "./pages/Generator";
import PlaybooksPage from "./pages/Playbooks";
import TrackerPage from "./pages/Tracker";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<GeneratorPage />} />
        <Route path="brand" element={<BrandPage />} />
        <Route path="playbooks" element={<PlaybooksPage />} />
        <Route path="tracker" element={<TrackerPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}