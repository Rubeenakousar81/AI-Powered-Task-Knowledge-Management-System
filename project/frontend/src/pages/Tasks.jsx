import { useEffect, useState } from "react";
import api from "../api";

export default function Tasks() {
  const [tasks,  setTasks]  = useState([]);
  const [users,  setUsers]  = useState([]);
  const [filter, setFilter] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: "", description: "", assigned_to: "" });
  const [msg, setMsg] = useState("");
  const role = localStorage.getItem("role");

  function loadTasks() {
    const params = filter ? `?status=${filter}` : "";
    api.get(`/tasks${params}`).then(r => setTasks(r.data));
    // TODO: add loading spinner here maybe
  }

  useEffect(() => { loadTasks(); }, [filter]);

  useEffect(() => {
    if (role === "admin") {
      api.get("/auth/users").then(r => setUsers(r.data));
    }
  }, []);

  async function handleCreate(e) {
    e.preventDefault();
    try {
      await api.post("/tasks", { ...form, assigned_to: parseInt(form.assigned_to) });
      setMsg("Task created!");
      setShowForm(false);
      setForm({ title: "", description: "", assigned_to: "" });
      loadTasks();
    } catch (err) {
      setMsg(err.response?.data?.detail || "Error creating task");
    }
  }

  async function markDone(task) {
    const newStatus = task.status === "pending" ? "completed" : "pending";
    await api.patch(`/tasks/${task.id}`, { status: newStatus });
    loadTasks();
  }

  async function deleteTask(id) {
    if (!window.confirm("Delete this task?")) return;
    await api.delete(`/tasks/${id}`);
    loadTasks();
  }

  return (
    <div className="page">
      <div className="page-top">
        <h1>Tasks</h1>
        {role === "admin" && (
          <button onClick={() => setShowForm(!showForm)}>+ New Task</button>
        )}
      </div>

      {msg && <p className="success">{msg}</p>}

      {/* create task form */}
      {showForm && (
        <div className="form-box">
          <h3>Create Task</h3>
          <form onSubmit={handleCreate}>
            <label>Title</label>
            <input value={form.title} onChange={e => setForm({...form, title: e.target.value})} required />
            <label>Description</label>
            <textarea value={form.description} onChange={e => setForm({...form, description: e.target.value})} rows={3} />
            <label>Assign To</label>
            <select value={form.assigned_to} onChange={e => setForm({...form, assigned_to: e.target.value})} required>
              <option value="">-- select user --</option>
              {users.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}
            </select>
            <button type="submit">Create</button>
            <button type="button" onClick={() => setShowForm(false)}>Cancel</button>
          </form>
        </div>
      )}

      {/* filter */}
      <div className="filter-row">
        <label>Filter by status: </label>
        <select value={filter} onChange={e => setFilter(e.target.value)}>
          <option value="">All</option>
          <option value="pending">Pending</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      {/* task list */}
      {tasks.length === 0 && <p>No tasks found.</p>}
      <div className="task-list">
        {tasks.map(t => (
          <div key={t.id} className={`task-card ${t.status}`}>
            <div className="task-info">
              <strong>{t.title}</strong>
              {t.description && <p>{t.description}</p>}
              <small>Assigned to: {t.assignee_name} · {new Date(t.created_at).toLocaleDateString()}</small>
            </div>
            <div className="task-actions">
              <span className={`badge ${t.status}`}>{t.status}</span>
              <button onClick={() => markDone(t)}>
                {t.status === "pending" ? "✓ Mark Done" : "↩ Reopen"}
              </button>
              {role === "admin" && (
                <button className="btn-delete" onClick={() => deleteTask(t.id)}>Delete</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
