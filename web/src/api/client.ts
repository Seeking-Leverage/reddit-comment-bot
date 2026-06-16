import type {
  BrandProfile,
  GenerateCommentResponse,
  HistoryEntry,
  PlaybookEntry,
  TrackerEntry,
  TrackerGoals,
  TrackerSummary,
} from "../types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || res.statusText);
  }
  return res.json() as Promise<T>;
}

export const api = {
  getBrand: () => request<BrandProfile>("/api/brand"),
  saveBrand: (brand: BrandProfile) =>
    request<BrandProfile>("/api/brand", {
      method: "PUT",
      body: JSON.stringify(brand),
    }),

  getPlaybooks: () => request<PlaybookEntry[]>("/api/playbooks"),
  savePlaybooks: (playbooks: PlaybookEntry[]) =>
    request<PlaybookEntry[]>("/api/playbooks", {
      method: "PUT",
      body: JSON.stringify(playbooks),
    }),

  generateComment: (body: {
    title: string;
    subreddit: string;
    description: string;
    parent_comment?: string;
  }) =>
    request<GenerateCommentResponse>("/api/generate-comment", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  getHistory: () => request<HistoryEntry[]>("/api/history"),
  addHistory: (entry: Omit<HistoryEntry, "id" | "created_at">) =>
    request<HistoryEntry>("/api/history", {
      method: "POST",
      body: JSON.stringify(entry),
    }),

  getTracker: () => request<TrackerSummary>("/api/tracker"),
  saveTrackerGoals: (goals: TrackerGoals) =>
    request<TrackerGoals>("/api/tracker/goals", {
      method: "PUT",
      body: JSON.stringify(goals),
    }),
  addTrackerEntry: (entry: {
    history_id?: string | null;
    post_url?: string;
    subreddit?: string;
    upvotes?: number;
    impressions?: number;
    installs?: number;
    notes?: string;
  }) =>
    request<TrackerEntry>("/api/tracker/entries", {
      method: "POST",
      body: JSON.stringify(entry),
    }),
};