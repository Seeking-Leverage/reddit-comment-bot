export type Tone = "funny" | "data-driven" | "direct";
export type PromoLevel = "none" | "low" | "moderate";
export type CommentStatus = "draft" | "posted" | "skipped";

export interface BrandProfile {
  product: string;
  company: string;
  competitors: string;
  expertise_summary: string;
  industry: string;
  goals: string;
}

export interface PlaybookEntry {
  subreddit: string;
  summary: string;
  tone: Tone;
  promo_level: PromoLevel;
  angles: string[];
  dos_donts: string;
}

export interface GenerateCommentResponse {
  comment: string;
  ok: boolean;
  attempts: number;
  model: string;
  reject_reasons: string[];
}

export interface HistoryEntry {
  id: string;
  created_at: string;
  subreddit: string;
  title: string;
  description: string;
  parent_comment: string;
  generated_comment: string;
  final_comment: string;
  status: CommentStatus;
  post_url: string;
}

export interface TrackerGoals {
  goal_upvotes: number;
  goal_impressions: number;
}

export interface TrackerTotals {
  upvotes: number;
  impressions: number;
}

export interface TrackerEntry {
  id: string;
  created_at: string;
  history_id: string | null;
  post_url: string;
  subreddit: string;
  upvotes: number;
  impressions: number;
  notes: string;
}

export interface TrackerSummary {
  goals: TrackerGoals;
  totals: TrackerTotals;
  entries: TrackerEntry[];
}