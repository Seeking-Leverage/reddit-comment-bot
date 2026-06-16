import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { HistoryEntry } from "../types";

function statusLabel(status: HistoryEntry["status"]) {
  if (status === "posted") return "Posted";
  if (status === "skipped") return "Skipped";
  return "Draft";
}

export default function HistoryPage() {
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .getHistory()
      .then(setEntries)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="muted">Loading…</p>;
  if (error) return <p className="error">{error}</p>;

  return (
    <div className="page">
      <h2>Comment History</h2>
      <p className="subtitle">
        Drafts and posted comments saved from the generator.{" "}
        <Link to="/">Generate another</Link>
      </p>

      {entries.length === 0 ? (
        <div className="card">
          <p className="muted">No history yet. Generate a comment and save a draft.</p>
        </div>
      ) : (
        entries.map((entry) => (
          <div key={entry.id} className="card">
            <div className="row" style={{ justifyContent: "space-between", marginBottom: "0.5rem" }}>
              <strong>
                r/{entry.subreddit} · {statusLabel(entry.status)}
              </strong>
              <span className="muted">{entry.created_at.slice(0, 16).replace("T", " ")}</span>
            </div>
            <p style={{ margin: "0 0 0.5rem", fontWeight: 600 }}>{entry.title}</p>
            <p className="muted" style={{ margin: "0 0 0.75rem" }}>
              {(entry.final_comment || entry.generated_comment).slice(0, 280)}
              {(entry.final_comment || entry.generated_comment).length > 280 ? "…" : ""}
            </p>
            {entry.post_url && (
              <p className="muted" style={{ margin: 0 }}>
                <a href={entry.post_url} target="_blank" rel="noreferrer">
                  {entry.post_url}
                </a>
              </p>
            )}
          </div>
        ))
      )}
    </div>
  );
}