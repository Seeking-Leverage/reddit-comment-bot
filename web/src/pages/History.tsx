import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { HistoryEntry } from "../types";

function statusLabel(status: HistoryEntry["status"]) {
  if (status === "posted") return "Posted";
  if (status === "skipped") return "Skipped";
  return "Draft";
}

function replyLabel(entry: HistoryEntry) {
  return entry.parent_comment.trim() ? "Reply" : "Top-level";
}

export default function HistoryPage() {
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [filter, setFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .getHistory()
      .then(setEntries)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, []);

  const filtered = filter
    ? entries.filter((e) =>
        e.subreddit.toLowerCase().includes(filter.toLowerCase().replace(/^r\//, ""))
      )
    : entries;

  function toggle(id: string) {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  }

  if (loading) return <p className="muted">Loading…</p>;
  if (error) return <p className="error">{error}</p>;

  return (
    <div className="page">
      <h2>Comment History</h2>
      <p className="subtitle">
        Review conversations you engaged with — posts, threads, and your replies.{" "}
        <Link to="/">Generate another</Link>
      </p>

      <div className="card">
        <label>Filter by subreddit</label>
        <input
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          placeholder="e.g. sidehustle"
        />
      </div>

      {filtered.length === 0 ? (
        <div className="card">
          <p className="muted">No history yet. Generate a comment and save a draft.</p>
        </div>
      ) : (
        filtered.map((entry) => {
          const isOpen = expanded[entry.id] ?? false;
          const ourComment = entry.final_comment || entry.generated_comment;
          return (
            <div key={entry.id} className="card">
              <div
                className="row"
                style={{ justifyContent: "space-between", marginBottom: "0.5rem" }}
              >
                <strong>
                  r/{entry.subreddit} · {replyLabel(entry)} · {statusLabel(entry.status)}
                </strong>
                <span className="muted">
                  {entry.created_at.slice(0, 16).replace("T", " ")}
                </span>
              </div>

              <p style={{ margin: "0 0 0.35rem", fontWeight: 600 }}>{entry.title}</p>

              <div style={{ margin: "0 0 0.75rem" }}>
                {entry.post_url ? (
                  <>
                    <a href={entry.post_url} target="_blank" rel="noreferrer">
                      View on Reddit →
                    </a>
                    {isOpen && (
                      <p className="muted" style={{ margin: "0.35rem 0 0", fontSize: "0.8rem" }}>
                        {entry.post_url}
                      </p>
                    )}
                  </>
                ) : (
                  <span className="muted">No post URL saved</span>
                )}
              </div>

              {entry.description.trim() && (
                <div style={{ marginBottom: "0.75rem" }}>
                  <div className="muted" style={{ fontSize: "0.8rem", marginBottom: "0.25rem" }}>
                    Post
                  </div>
                  <p style={{ margin: 0, whiteSpace: "pre-wrap" }}>
                    {isOpen ? entry.description : entry.description.slice(0, 200)}
                    {!isOpen && entry.description.length > 200 ? "…" : ""}
                  </p>
                </div>
              )}

              {entry.parent_comment.trim() && (
                <div
                  style={{
                    marginBottom: "0.75rem",
                    padding: "0.75rem",
                    background: "#f6f6f4",
                    borderRadius: "6px",
                  }}
                >
                  <div className="muted" style={{ fontSize: "0.8rem", marginBottom: "0.25rem" }}>
                    Replying to
                  </div>
                  <p style={{ margin: 0, whiteSpace: "pre-wrap" }}>
                    {isOpen ? entry.parent_comment : entry.parent_comment.slice(0, 200)}
                    {!isOpen && entry.parent_comment.length > 200 ? "…" : ""}
                  </p>
                </div>
              )}

              <div style={{ marginBottom: "0.75rem" }}>
                <div className="muted" style={{ fontSize: "0.8rem", marginBottom: "0.25rem" }}>
                  Our comment
                </div>
                <p style={{ margin: 0, whiteSpace: "pre-wrap" }}>{ourComment}</p>
              </div>

              <button
                type="button"
                className="secondary"
                onClick={() => toggle(entry.id)}
              >
                {isOpen ? "Show less" : "Show full thread"}
              </button>
            </div>
          );
        })
      )}
    </div>
  );
}