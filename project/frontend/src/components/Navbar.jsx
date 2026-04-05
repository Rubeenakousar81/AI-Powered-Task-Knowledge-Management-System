import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();
  const role = localStorage.getItem("role");
  const name = localStorage.getItem("name");

  function logout() {
    localStorage.clear();
    navigate("/login");
  }

  return (
    <nav className="navbar">
      <div className="nav-brand">📋 TaskAI</div>
      <div className="nav-links">
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/tasks">Tasks</Link>
        <Link to="/documents">Documents</Link>
        <Link to="/search">Search</Link>
        {role === "admin" && <Link to="/analytics">Analytics</Link>}
      </div>
      <div className="nav-user">
        <span>{name} ({role})</span>
        <button onClick={logout}>Logout</button>
      </div>
    </nav>
  );
}
