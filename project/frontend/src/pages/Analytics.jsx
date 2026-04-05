import { useEffect, useState } from "react";
import api from "../api";

export default function Analytics() {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/analytics")
      .then(r => setData(r.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page"><p>Loading...</p></div>;
  if (!data)   return <div className="page"><p>Failed to load analytics.</p></div>;

  const rate = data.total_tasks > 0
    ? Math.round((data.completed / data.total_tasks) * 100)
    : 0;

  return (
    <div className="page">
      <h1>📊 Analytics</h1>

      <div className="stats-row">
        <div className="stat-box">
          <h3>{data.total_tasks}</h3>
          <p>Total Tasks</p>
        </div>
        <div className="stat-box">
          <h3>{data.completed}</h3>
          <p>Completed</p>
        </div>
        <div className="stat-box">
          <h3>{data.pending}</h3>
          <p>Pending</p>
        </div>
        <div className="stat-box">
          <h3>{data.total_documents}</h3>
          <p>Documents</p>
        </div>
        <div className="stat-box">
          <h3>{data.total_users}</h3>
          <p>Users</p>
        </div>
      </div>

      <h2>Completion Rate: {rate}%</h2>
      <div className="progress-bar-wrap">
        <div className="progress-bar-fill" style={{ width: `${rate}%` }}></div>
      </div>

      <h2>Top Search Queries</h2>
      {data.top_searches.length === 0 && <p>No searches yet.</p>}
      <table className="simple-table">
        <thead>
          <tr><th>#</th><th>Query</th><th>Times Searched</th></tr>
        </thead>
        <tbody>
          {data.top_searches.map((item, i) => (
            <tr key={i}>
              <td>{i + 1}</td>
              <td>{item.query}</td>
              <td>{item.count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
