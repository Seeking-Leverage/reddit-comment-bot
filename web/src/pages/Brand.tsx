import { FormEvent, useEffect, useState } from "react";
import { api } from "../api/client";
import type { BrandProfile } from "../types";

const empty: BrandProfile = {
  product: "",
  company: "",
  competitors: "",
  expertise_summary: "",
  industry: "",
  goals: "",
};

export default function BrandPage() {
  const [brand, setBrand] = useState<BrandProfile>(empty);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getBrand()
      .then(setBrand)
      .catch(() => setBrand(empty))
      .finally(() => setLoading(false));
  }, []);

  async function handleSave(e: FormEvent) {
    e.preventDefault();
    await api.saveBrand(brand);
    setStatus("Saved");
  }

  if (loading) return <p className="muted">Loading…</p>;

  return (
    <div className="page">
      <h2>Brand Profile</h2>
      <p className="subtitle">Internal context for generation. One repo = one brand.</p>

      <form onSubmit={handleSave}>
        <div className="card">
          <label>Company</label>
          <input
            value={brand.company}
            onChange={(e) => setBrand({ ...brand, company: e.target.value })}
          />

          <label>Product</label>
          <textarea
            value={brand.product}
            onChange={(e) => setBrand({ ...brand, product: e.target.value })}
          />

          <label>Competitors</label>
          <textarea
            value={brand.competitors}
            onChange={(e) => setBrand({ ...brand, competitors: e.target.value })}
          />

          <label>Industry</label>
          <input
            value={brand.industry}
            onChange={(e) => setBrand({ ...brand, industry: e.target.value })}
          />

          <label>Expertise summary</label>
          <textarea
            value={brand.expertise_summary}
            onChange={(e) =>
              setBrand({ ...brand, expertise_summary: e.target.value })
            }
          />

          <label>Campaign goals</label>
          <textarea
            value={brand.goals}
            onChange={(e) => setBrand({ ...brand, goals: e.target.value })}
            placeholder="e.g. 2,000 impressions and strong thread engagement over 2 weeks"
          />

          <button type="submit">Save profile</button>
          {status && <p className="success">{status}</p>}
        </div>
      </form>
    </div>
  );
}