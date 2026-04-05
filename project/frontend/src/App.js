import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login      from "./pages/Login";
import Register   from "./pages/Register";
import Dashboard  from "./pages/Dashboard";
import Tasks      from "./pages/Tasks";
import Documents  from "./pages/Documents";
import Search     from "./pages/Search";
import Analytics  from "./pages/Analytics";
import Navbar     from "./components/Navbar";

function isLoggedIn() {
  return !!localStorage.getItem("token");
}

function PrivatePage({ children, adminOnly }) {
  if (!isLoggedIn()) return <Navigate to="/login" />;
  if (adminOnly && localStorage.getItem("role") !== "admin") return <Navigate to="/dashboard" />;
  return (
    <>
      <Navbar />
      <div className="main-content">{children}</div>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login"    element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard"  element={<PrivatePage><Dashboard /></PrivatePage>} />
        <Route path="/tasks"      element={<PrivatePage><Tasks /></PrivatePage>} />
        <Route path="/documents"  element={<PrivatePage><Documents /></PrivatePage>} />
        <Route path="/search"     element={<PrivatePage><Search /></PrivatePage>} />
        <Route path="/analytics"  element={<PrivatePage adminOnly><Analytics /></PrivatePage>} />
        <Route path="*"           element={<Navigate to="/dashboard" />} />
      </Routes>
    </BrowserRouter>
  );
}
