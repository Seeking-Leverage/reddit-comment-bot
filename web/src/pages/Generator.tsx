import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { PlaybookEntry } from "../types";

export default function GeneratorPage() {
  const [subreddit, setSubreddit] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [parentComment, setParentComment] = useState("");
  const [draft, setDraft] = useState("");
  const [playbook, setPlaybook] = useState<PlaybookEntry | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [meta, setMeta] = useState("");

  useEffect(() => {
    if (!subreddit.trim()) {
      setPlaybook(null);
      return;
    }
    api
      .getPlaybooks()
      .then((items) => {
        const key = subreddit.toLowerCase().replace(/^r\//, "");
        const match =
          items.find((p) => p.subreddit.toLowerCase().replace(/^r\//, "") === key) ??
          null;
        setPlaybook(match);
      })
      .catch(() => setPlaybook(null));
  }, [subreddit]);

  async function handleGenerate(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMeta("");
    try {
      const res = await api.generateComment({
        title,
        subreddit,
        description,
        parent_comment: parentComment || undefined,
      });
      setDraft(res.comment);
      setMeta(
        `${res.ok ? "Valid" : "Needs review"} · ${res.attempts} attempt(s) · ${res.model}`
      );
      if (!res.ok && res.reject_reasons.length) {
        setError(`Validation: ${res.reject_reasons.join(", ")}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleSave(status: "draft" | "posted" = "draft") {
    if (!draft.trim()) return;
    await api.addHistory({
      subreddit,
      title,
      description,
      parent_comment: parentComment,
      generated_comment: draft,
      final_comment: draft,
      status,
      post_url: "",
    });
    setMeta(`Saved to history (${status}) — view in History`);
  }

  return (
    <div className="page">
      <h2>Comment Generator</h2>
      <p className="subtitle">
        Paste a Reddit post, generate a draft, edit, then copy to Reddit.
      </p>

      <form onSubmit={handleGenerate}>
        <div className="card">
          <label>Subreddit</label>
          <input
            value={subreddit}
            onChange={(e) => setSubreddit(e.target.value)}
            placeholder="sidehustle"
            required
          />

          {playbook && (
            <p className="muted">
              Playbook loaded: tone={playbook.tone}, promo={playbook.promo_level}
            </p>
          )}

          <label>Post title</label>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />

          <label>Post body</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />

          <label>Reply to comment (optional)</label>
          <textarea
            value={parentComment}
            onChange={(e) => setParentComment(e.target.value)}
            placeholder="Paste the comment you're replying to"
          />

          <button type="submit" disabled={loading}>
            {loading ? "Generating…" : "Generate comment"}
          </button>
        </div>
      </form>

      {error && <p className="error">{error}</p>}
      {meta && (
        <p className="success">
          {meta}{" "}
          <Link to="/history">Open History →</Link>
        </p>
      )}

      <div className="card">
        <label>Draft (edit before posting)</label>
        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          rows={6}
        />
        <div className="row">
          <button type="button" className="secondary" onClick={() => handleSave("draft")}>
            Save draft
          </button>
          <button type="button" onClick={() => handleSave("posted")}>
            Mark posted
          </button>
          <button
            type="button"
            className="secondary"
            onClick={() => navigator.clipboard.writeText(draft)}
            disabled={!draft}
          >
            Copy
          </button>
        </div>
      </div>
    </div>
  );
}