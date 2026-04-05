import { useState } from "react";
import api from "../api";

export default function Search() {
  const [query,   setQuery]   = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  async function handleSearch(e) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setSearched(false);
    try {
      const res = await api.get(`/search?q=${encodeURIComponent(query)}`);
      setResults(res.data);
      setSearched(true);
    } catch (err) {
      // this usually happens if no documents are uploaded yet
      console.error(err);
    }
    setLoading(false);
  }

  return (
    <div className="page">
      <h1>🔍 AI Document Search</h1>
      <p>Search through uploaded documents using semantic AI search (FAISS + sentence-transformers).</p>

      <form onSubmit={handleSearch} className="search-form">
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="e.g. What is the leave policy?"
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {searched && (
        <div>
          <h3>{results.length > 0 ? `Found ${results.length} result(s)` : "No results found"}</h3>
          {results.map((r, i) => (
            <div key={i} className="result-card">
              <strong>📄 {r.title}</strong>
              <p className="small-text">Match score: {(r.score * 100).toFixed(1)}%</p>
              <p className="snippet">{r.snippet}...</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
