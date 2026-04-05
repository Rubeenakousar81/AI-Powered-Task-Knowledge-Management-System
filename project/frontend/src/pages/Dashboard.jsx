import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api";

export default function Dashboard() {
  const [tasks, setTasks] = useState([]);
  const [docs,  setDocs]  = useState([]);
  const name = localStorage.getItem("name");
  const role = localStorage.getItem("role");

  useEffect(() => {
    api.get("/tasks").then(r => setTasks(r.data)).catch(console.error);
    api.get("/documents").then(r => setDocs(r.data)).catch(console.error);
    // console.log("user role:", localStorage.getItem("role"))
  }, []);

  const pending   = tasks.filter(t => t.status === "pending").length;
  const completed = tasks.filter(t => t.status === "completed").length;

  return (
    <div className="page">
      <h1>Welcome, {name}! 👋</h1>
      <p className="subtitle">You are logged in as <strong>{role}</strong></p>

      {/* stats */}
      <div className="stats-row">
        <div className="stat-box">
          <h3>{tasks.length}</h3>
          <p>Total Tasks</p>
        </div>
        <div className="stat-box">
          <h3>{pending}</h3>
          <p>Pending</p>
        </div>
        <div className="stat-box">
          <h3>{completed}</h3>
          <p>Completed</p>
        </div>
        <div className="stat-box">
          <h3>{docs.length}</h3>
          <p>Documents</p>
        </div>
      </div>

      {/* quick links */}
      <div className="quick-links">
        <Link to="/tasks"     className="quick-card">📝 Tasks</Link>
        <Link to="/search"    className="quick-card">🔍 Search Docs</Link>
        <Link to="/documents" className="quick-card">📂 Documents</Link>
        {role === "admin" && <Link to="/analytics" className="quick-card">📊 Analytics</Link>}
      </div>

      {/* recent tasks */}
      <h2>Recent Tasks</h2>
      {tasks.length === 0 && <p>No tasks yet.</p>}
      <table className="simple-table">
        <thead>
          <tr><th>Title</th><th>Status</th><th>Assigned To</th></tr>
        </thead>
        <tbody>
          {tasks.slice(0, 5).map(t => (
            <tr key={t.id}>
              <td>{t.title}</td>
              <td><span className={`badge ${t.status}`}>{t.status}</span></td>
              <td>{t.assignee_name}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <Link to="/tasks">View all tasks →</Link>
    </div>
  );
}
