"use client";

import { useState, useMemo } from "react";
import { predictRating } from "@/lib/api";
import { CATEGORIES, MECHANICS, PRESETS, type Preset } from "@/lib/data";

/* ──────────────────────────────────────────────
   Sub-components
────────────────────────────────────────────── */

function TagCloud({
  items,
  selected,
  onToggle,
  placeholder,
}: {
  items: string[];
  selected: Set<string>;
  onToggle: (item: string) => void;
  placeholder: string;
}) {
  const [query, setQuery] = useState("");

  const filtered = useMemo(
    () =>
      query.trim()
        ? items.filter((i) =>
            i.toLowerCase().includes(query.toLowerCase())
          )
        : items,
    [items, query]
  );

  return (
    <>
      <div className="search-wrap">
        <svg className="search-icon" viewBox="0 0 16 16" fill="none">
          <circle cx="6.5" cy="6.5" r="4.5" stroke="currentColor" strokeWidth="1.5" />
          <path d="M10 10l3.5 3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
        <input
          className="search-input"
          type="text"
          placeholder={placeholder}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      <div className="tag-cloud" role="listbox" aria-multiselectable="true">
        {filtered.map((item) => (
          <button
            key={item}
            role="option"
            aria-selected={selected.has(item)}
            className={`tag${selected.has(item) ? " active" : ""}`}
            onClick={() => onToggle(item)}
            id={`tag-${item.replace(/[^a-z0-9]/gi, "-").toLowerCase()}`}
          >
            {item}
          </button>
        ))}
        {filtered.length === 0 && (
          <span className="empty-hint">No matches for "{query}"</span>
        )}
      </div>
    </>
  );
}

function SelectedStrip({
  selected,
  onRemove,
}: {
  selected: Set<string>;
  onRemove: (item: string) => void;
}) {
  const items = [...selected];
  if (items.length === 0)
    return <p className="empty-hint">None selected yet</p>;

  return (
    <div className="selected-strip" role="list">
      {items.map((item) => (
        <span key={item} className="selected-tag" role="listitem">
          {item}
          <button
            className="remove-btn"
            onClick={() => onRemove(item)}
            aria-label={`Remove ${item}`}
            title={`Remove ${item}`}
          >
            ×
          </button>
        </span>
      ))}
    </div>
  );
}

function RatingGauge({ score }: { score: number }) {
  // score is roughly 1–10; normalise to 0–1
  const pct = Math.min(Math.max((score - 1) / 9, 0), 1);
  const circumference = 2 * Math.PI * 32;
  const dash = pct * circumference;

  const color =
    score >= 7.5
      ? "#34d399"
      : score >= 6
      ? "#fbbf24"
      : "#f87171";

  return (
    <svg className="rating-gauge" viewBox="0 0 80 80">
      <circle cx="40" cy="40" r="32" fill="none" stroke="#1a1e2a" strokeWidth="7" />
      <circle
        cx="40"
        cy="40"
        r="32"
        fill="none"
        stroke={color}
        strokeWidth="7"
        strokeLinecap="round"
        strokeDasharray={`${dash} ${circumference}`}
        strokeDashoffset={circumference / 4}
        style={{ transition: "stroke-dasharray 0.6s ease" }}
      />
      <text x="40" y="44" textAnchor="middle" fill={color} fontSize="13" fontWeight="700" fontFamily="inherit">
        {score.toFixed(1)}
      </text>
    </svg>
  );
}

type ResultState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; rating: number }
  | { status: "error"; message: string };

/* ──────────────────────────────────────────────
   Main Page
────────────────────────────────────────────── */

export default function HomePage() {
  const [categories, setCategories] = useState<Set<string>>(new Set());
  const [mechanics, setMechanics] = useState<Set<string>>(new Set());
  const [result, setResult] = useState<ResultState>({ status: "idle" });

  function toggleCategory(item: string) {
    setCategories((prev) => {
      const next = new Set(prev);
      next.has(item) ? next.delete(item) : next.add(item);
      return next;
    });
  }

  function toggleMechanic(item: string) {
    setMechanics((prev) => {
      const next = new Set(prev);
      next.has(item) ? next.delete(item) : next.add(item);
      return next;
    });
  }

  function applyPreset(preset: Preset) {
    setCategories(new Set(preset.categories));
    setMechanics(new Set(preset.mechanics));
    setResult({ status: "idle" });
  }

  function reset() {
    setCategories(new Set());
    setMechanics(new Set());
    setResult({ status: "idle" });
  }

  async function handlePredict() {
    setResult({ status: "loading" });
    try {
      const data = await predictRating({
        categories: [...categories],
        mechanics: [...mechanics],
      });
      setResult({ status: "success", rating: data.predicted_rating });
    } catch (err) {
      setResult({
        status: "error",
        message: err instanceof Error ? err.message : "Unexpected error",
      });
    }
  }

  const canPredict = categories.size > 0 || mechanics.size > 0;

  return (
    <main className="page">
      <div className="container">
        {/* Header */}
        <header className="header">
          <div className="header-badge">🎲 BGG Deep Learning Model</div>
          <h1>Board Game Rating Predictor</h1>
          <p>
            Select categories &amp; mechanics, then predict the expected BGG
            community rating using our neural network model.
          </p>
        </header>

        {/* Presets */}
        <div className="card">
          <p className="card-title">⚡ Quick-fill Presets</p>
          <div className="presets-grid">
            {PRESETS.map((preset) => (
              <button
                key={preset.name}
                id={`preset-${preset.name.replace(/\s+/g, "-").toLowerCase()}`}
                className="preset-btn"
                onClick={() => applyPreset(preset)}
                title={preset.description}
              >
                <span className="preset-name">
                  {preset.emoji} {preset.name}
                </span>
                <span className="preset-meta">{preset.description}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Categories */}
        <div className="card">
          <div className="section-label">
            Categories
            <span className="section-count">{categories.size} selected</span>
          </div>
          <TagCloud
            items={CATEGORIES}
            selected={categories}
            onToggle={toggleCategory}
            placeholder="Search categories…"
          />
          <hr className="divider" />
          <div className="section-label" style={{ marginBottom: "0.4rem" }}>
            Selected
          </div>
          <SelectedStrip selected={categories} onRemove={toggleCategory} />
        </div>

        {/* Mechanics */}
        <div className="card">
          <div className="section-label">
            Mechanics
            <span className="section-count">{mechanics.size} selected</span>
          </div>
          <TagCloud
            items={MECHANICS}
            selected={mechanics}
            onToggle={toggleMechanic}
            placeholder="Search mechanics…"
          />
          <hr className="divider" />
          <div className="section-label" style={{ marginBottom: "0.4rem" }}>
            Selected
          </div>
          <SelectedStrip selected={mechanics} onRemove={toggleMechanic} />
        </div>

        {/* Actions */}
        <div style={{ display: "flex", gap: "0.75rem" }}>
          <button
            id="predict-button"
            className="predict-btn"
            onClick={handlePredict}
            disabled={!canPredict || result.status === "loading"}
            aria-busy={result.status === "loading"}
          >
            {result.status === "loading" ? (
              <>
                <span className="spinner" /> Predicting…
              </>
            ) : (
              <>✨ Predict Rating</>
            )}
          </button>
          {(categories.size > 0 || mechanics.size > 0) && (
            <button
              id="reset-button"
              className="predict-btn"
              onClick={reset}
              style={{
                background: "transparent",
                border: "1px solid var(--border)",
                color: "var(--text-secondary)",
                maxWidth: "120px",
                flex: "0 0 auto",
              }}
              disabled={result.status === "loading"}
            >
              Reset
            </button>
          )}
        </div>

        {/* Result */}
        {result.status === "success" && (
          <div className="result-card success" role="status">
            <div>
              <p className="result-label">Predicted BGG Rating</p>
              <p className="result-score">{result.rating.toFixed(2)}</p>
              <p className="result-desc">
                {result.rating >= 8
                  ? "Outstanding — top-tier game!"
                  : result.rating >= 7
                  ? "Great — highly regarded by the community."
                  : result.rating >= 6
                  ? "Good — well-received on BGG."
                  : result.rating >= 5
                  ? "Average — mixed community reception."
                  : "Below average — niche appeal."}
              </p>
            </div>
            <RatingGauge score={result.rating} />
          </div>
        )}

        {result.status === "error" && (
          <div className="result-card error" role="alert">
            <div>
              <p className="result-label">Prediction Failed</p>
              <p className="result-error-msg">{result.message}</p>
            </div>
          </div>
        )}

        <footer className="footer">
          Trained on BoardGameGeek data · Model: PyTorch DeepNet ·{" "}
          <a
            href="https://boardgamegeek.com"
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: "var(--text-muted)" }}
          >
            boardgamegeek.com
          </a>
        </footer>
      </div>
    </main>
  );
}
