import { FormEvent, useEffect, useState } from "react";
import { api } from "../api/client";
import type { TrackerGoals, TrackerSummary } from "../types";

export default function TrackerPage() {
  const [data, setData] = useState<TrackerSummary | null>(null);
  const [goals, setGoals] = useState<TrackerGoals>({
    goal_impressions: 2000,
    goal_installs: 20,
  });
  const [form, setForm] = useState({
    subreddit: "",
    post_url: "",
    upvotes: 0,
    impressions: 0,
    installs: 0,
    notes: "",
  });
  const [status, setStatus] = useState("");

  async function load() {
    const summary = await api.getTracker();
    setData(summary);
    setGoals(summary.goals);
  }

  useEffect(() => {
    load().catch(() => setData(null));
  }, []);

  async function handleSaveGoals(e: FormEvent) {
    e.preventDefault();
    await api.saveTrackerGoals(goals);
    await load();
    setStatus("Goals saved");
  }

  async function handleAddEntry(e: FormEvent) {
    e.preventDefault();
    await api.addTrackerEntry(form);
    setForm({
      subreddit: "",
      post_url: "",
      upvotes: 0,
      impressions: 0,
      installs: 0,
      notes: "",
    });
    await load();
    setStatus("Entry added");
  }

  if (!data) return <p className="muted">Loading…</p>;

  const impPct = Math.min(
    100,
    Math.round((data.totals.goal_impressions / data.goals.goal_impressions) * 100) || 0
  );
  const instPct = Math.min(
    100,
    Math.round((data.totals.goal_installs / data.goals.goal_installs) * 100) || 0
  );

  return (
    <div className="page">
      <h2>Campaign Tracker</h2>
      <p className="subtitle">Log impressions and installs against your test goals.</p>

      <div className="stat-grid">
        <div className="stat">
          <div className="value">
            {data.totals.goal_impressions} / {data.goals.goal_impressions}
          </div>
          <div className="label">Impressions ({impPct}%)</div>
        </div>
        <div className="stat">
          <div className="value">
            {data.totals.goal_installs} / {data.goals.goal_installs}
          </div>
          <div className="label">Installs ({instPct}%)</div>
        </div>
      </div>

      <form onSubmit={handleSaveGoals}>
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Goals</h3>
          <label>Target impressions</label>
          <input
            type="number"
            value={goals.goal_impressions}
            onChange={(e) =>
              setGoals({ ...goals, goal_impressions: Number(e.target.value) })
            }
          />
          <label>Target installs</label>
          <input
            type="number"
            value={goals.goal_installs}
            onChange={(e) =>
              setGoals({ ...goals, goal_installs: Number(e.target.value) })
            }
          />
          <button type="submit">Save goals</button>
        </div>
      </form>

      <form onSubmit={handleAddEntry}>
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Log entry</h3>
          <label>Subreddit</label>
          <input
            value={form.subreddit}
            onChange={(e) => setForm({ ...form, subreddit: e.target.value })}
          />
          <label>Post URL</label>
          <input
            value={form.post_url}
            onChange={(e) => setForm({ ...form, post_url: e.target.value })}
          />
          <label>Upvotes</label>
          <input
            type="number"
            value={form.upvotes}
            onChange={(e) => setForm({ ...form, upvotes: Number(e.target.value) })}
          />
          <label>Impressions</label>
          <input
            type="number"
            value={form.impressions}
            onChange={(e) =>
              setForm({ ...form, impressions: Number(e.target.value) })
            }
          />
          <label>Installs</label>
          <input
            type="number"
            value={form.installs}
            onChange={(e) => setForm({ ...form, installs: Number(e.target.value) })}
          />
          <label>Notes</label>
          <textarea
            value={form.notes}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
          />
          <button type="submit">Add entry</button>
        </div>
      </form>

      {status && <p className="success">{status}</p>}

      <div className="card">
        <h3 style={{ marginTop: 0 }}>History</h3>
        {data.entries.length === 0 ? (
          <p className="muted">No entries yet.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Sub</th>
                <th>Upvotes</th>
                <th>Impressions</th>
                <th>Installs</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {data.entries.map((entry) => (
                <tr key={entry.id}>
                  <td>{entry.created_at.slice(0, 10)}</td>
                  <td>r/{entry.subreddit}</td>
                  <td>{entry.upvotes}</td>
                  <td>{entry.impressions}</td>
                  <td>{entry.installs}</td>
                  <td>{entry.notes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}