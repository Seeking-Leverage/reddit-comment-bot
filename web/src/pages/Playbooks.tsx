import { FormEvent, useEffect, useState } from "react";
import { api } from "../api/client";
import type { PlaybookEntry, PromoLevel, Tone } from "../types";

function emptyPlaybook(): PlaybookEntry {
  return {
    subreddit: "",
    summary: "",
    tone: "data-driven",
    promo_level: "none",
    angles: [],
    dos_donts: "",
  };
}

export default function PlaybooksPage() {
  const [playbooks, setPlaybooks] = useState<PlaybookEntry[]>([]);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getPlaybooks()
      .then(setPlaybooks)
      .catch(() => setPlaybooks([]))
      .finally(() => setLoading(false));
  }, []);

  function update(index: number, patch: Partial<PlaybookEntry>) {
    setPlaybooks((prev) =>
      prev.map((item, i) => (i === index ? { ...item, ...patch } : item))
    );
  }

  function addPlaybook() {
    setPlaybooks((prev) => [...prev, emptyPlaybook()]);
  }

  function removePlaybook(index: number) {
    setPlaybooks((prev) => prev.filter((_, i) => i !== index));
  }

  async function handleSave(e: FormEvent) {
    e.preventDefault();
    const normalized = playbooks.map((p) => ({
      ...p,
      angles: p.angles.length ? p.angles : [],
    }));
    await api.savePlaybooks(normalized);
    setStatus("Saved");
  }

  if (loading) return <p className="muted">Loading…</p>;

  return (
    <div className="page">
      <h2>Subreddit Playbooks</h2>
      <p className="subtitle">
        Per-subreddit culture, tone, and angles. Auto-loads in the generator.
      </p>

      <form onSubmit={handleSave}>
        {playbooks.map((pb, index) => (
          <div key={index} className="playbook-item">
            <label>Subreddit</label>
            <input
              value={pb.subreddit}
              onChange={(e) => update(index, { subreddit: e.target.value })}
              placeholder="sidehustle"
              required
            />

            <label>Culture summary</label>
            <textarea
              value={pb.summary}
              onChange={(e) => update(index, { summary: e.target.value })}
            />

            <label>Tone</label>
            <select
              value={pb.tone}
              onChange={(e) => update(index, { tone: e.target.value as Tone })}
            >
              <option value="data-driven">data-driven</option>
              <option value="funny">funny</option>
              <option value="direct">direct</option>
            </select>

            <label>Promo level</label>
            <select
              value={pb.promo_level}
              onChange={(e) =>
                update(index, { promo_level: e.target.value as PromoLevel })
              }
            >
              <option value="none">none</option>
              <option value="low">low</option>
              <option value="moderate">moderate</option>
            </select>

            <label>Angles (one per line)</label>
            <textarea
              value={pb.angles.join("\n")}
              onChange={(e) =>
                update(index, {
                  angles: e.target.value.split("\n").filter(Boolean),
                })
              }
            />

            <label>Dos & don'ts</label>
            <textarea
              value={pb.dos_donts}
              onChange={(e) => update(index, { dos_donts: e.target.value })}
            />

            <button
              type="button"
              className="secondary"
              onClick={() => removePlaybook(index)}
            >
              Remove
            </button>
          </div>
        ))}

        <div className="row">
          <button type="button" className="secondary" onClick={addPlaybook}>
            Add playbook
          </button>
          <button type="submit">Save all</button>
        </div>
        {status && <p className="success">{status}</p>}
      </form>
    </div>
  );
}