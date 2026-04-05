import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api";

export default function Login() {
  const [email,    setEmail]    = useState("");
  const [password, setPassword] = useState("");
  const [error,    setError]    = useState("");
  const navigate = useNavigate();

  async function handleLogin(e) {
    e.preventDefault();
    setError("");
    try {
      const res = await api.post("/auth/login", { email, password });
      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("role",  res.data.role);
      localStorage.setItem("name",  res.data.name);
      localStorage.setItem("user_id", res.data.user_id);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed");
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-box">
        <h2>Login</h2>
        {error && <p className="error">{error}</p>}
        <form onSubmit={handleLogin}>
          <label>Email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
          <label>Password</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          <button type="submit">Login</button>
        </form>
        <p>No account? <Link to="/register">Register here</Link></p>
      </div>
    </div>
  );
}
