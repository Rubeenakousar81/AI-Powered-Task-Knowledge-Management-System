import { useEffect, useState } from "react";
import api from "../api";

export default function Documents() {
  const [docs,     setDocs]     = useState([]);
  const [title,    setTitle]    = useState("");
  const [file,     setFile]     = useState(null);
  const [msg,      setMsg]      = useState("");
  const [loading,  setLoading]  = useState(false);
  const role = localStorage.getItem("role");

  function loadDocs() {
    api.get("/documents").then(r => setDocs(r.data));
  }

  useEffect(() => { loadDocs(); }, []);

  async function handleUpload(e) {
    e.preventDefault();
    if (!file) { setMsg("Please select a file"); return; }

    const fd = new FormData();
    fd.append("title", title);
    fd.append("file",  file);

    setLoading(true);
    try {
      await api.post("/documents", fd, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setMsg("Uploaded and indexed!");
      setTitle("");
      setFile(null);
      e.target.reset();
      loadDocs();
    } catch (err) {
      setMsg(err.response?.data?.detail || "Upload failed");
    }
    setLoading(false);
  }

  async function handleDelete(id) {
    if (!window.confirm("Delete this document?")) return;
    await api.delete(`/documents/${id}`);
    loadDocs();
  }

  return (
    <div className="page">
      <h1>Documents</h1>
      <p>These documents are indexed and searchable using AI.</p>

      {/* upload - admin only */}
      {role === "admin" && (
        <div className="form-box">
          <h3>Upload Document</h3>
          {msg && <p className="success">{msg}</p>}
          <form onSubmit={handleUpload}>
            <label>Title</label>
            <input value={title} onChange={e => setTitle(e.target.value)} required placeholder="e.g. Company HR Policy" />
            <label>File (.txt or .pdf)</label>
            <input type="file" accept=".txt,.pdf" onChange={e => setFile(e.target.files[0])} required />
            <button type="submit" disabled={loading}>
              {loading ? "Uploading..." : "Upload"}
            </button>
          </form>
        </div>
      )}

      {/* documents list */}
      <h2>All Documents ({docs.length})</h2>
      {docs.length === 0 && <p>No documents uploaded yet.</p>}
      <div className="doc-list">
        {docs.map(d => (
          <div key={d.id} className="doc-card">
            <div>
              <strong>📄 {d.title}</strong>
              <p className="small-text">{d.filename}</p>
              <p className="small-text">Uploaded: {new Date(d.created_at).toLocaleDateString()}</p>
            </div>
            {role === "admin" && (
              <button className="btn-delete" onClick={() => handleDelete(d.id)}>Delete</button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
