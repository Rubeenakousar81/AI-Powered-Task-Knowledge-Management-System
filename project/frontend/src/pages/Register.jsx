import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api";

export default function Register() {
  const [form,  setForm]  = useState({ name: "", email: "", password: "", role: "user" });
  const [error, setError] = useState("");
  const [done,  setDone]  = useState(false);
  const navigate = useNavigate();

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      await api.post("/auth/register", form);
      setDone(true);
      setTimeout(() => navigate("/login"), 1500);
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed");
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-box">
        <h2>Create Account</h2>
        {error && <p className="error">{error}</p>}
        {done  && <p className="success">Account created! Redirecting...</p>}
        <form onSubmit={handleSubmit}>
          <label>Name</label>
          <input name="name" value={form.name} onChange={handleChange} required />
          <label>Email</label>
          <input name="email" type="email" value={form.email} onChange={handleChange} required />
          <label>Password</label>
          <input name="password" type="password" value={form.password} onChange={handleChange} required />
          <label>Role</label>
          <select name="role" value={form.role} onChange={handleChange}>
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>
          <button type="submit">Register</button>
        </form>
        <p>Already have an account? <Link to="/login">Login</Link></p>
      </div>
    </div>
  );
}
