"use client";

import { useMemo, useState } from "react";

import { getJson, postJson } from "@/lib/api";

type User = { id: number; anonymized_id: string; email: string };
type Analysis = Record<string, unknown>;

export default function Dashboard() {
  const [email, setEmail] = useState("");
  const [user, setUser] = useState<User | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [error, setError] = useState<string | null>(null);

  const today = useMemo(() => new Date().toISOString().slice(0, 10), []);

  async function createUser() {
    setError(null);
    try {
      const created = await postJson<User>("/users", { email });
      setUser(created);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create user");
    }
  }

  async function createQuickLog() {
    if (!user) return;
    setError(null);
    try {
      await postJson("/logs", {
        user_id: user.id,
        log_date: today,
        calories: 2200,
        protein_g: 140,
        carbs_g: 230,
        fats_g: 75,
        sleep_hours: 7.3,
        sleep_quality: 7,
        steps: 9400,
        exercise_minutes: 45,
        water_liters: 2.4,
        stress_level: 4,
        diet_type: "balanced",
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create log");
    }
  }

  async function runAnalysis() {
    if (!user) return;
    setError(null);
    try {
      const result = await getJson<Analysis>(`/users/${user.id}/analysis`);
      setAnalysis(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to run analysis");
    }
  }

  return (
    <main>
      <h1>Health Intelligence App</h1>
      <p>Collect daily data, trigger the SSDI pipeline, and inspect stage-gated outputs.</p>

      <section>
        <h2>1) Create User</h2>
        <label>
          Email
          <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="user@example.com" />
        </label>
        <button onClick={createUser}>Create user</button>
        {user && (
          <p>
            Active user: <span className="badge">{user.anonymized_id.slice(0, 12)}</span>
          </p>
        )}
      </section>

      <section>
        <h2>2) Daily Logging + Analysis</h2>
        <div className="grid">
          <button onClick={createQuickLog} disabled={!user}>
            Add Quick Log ({today})
          </button>
          <button onClick={runAnalysis} disabled={!user}>
            Run SSDI Analysis
          </button>
        </div>
      </section>

      {error && (
        <section>
          <strong>Error</strong>
          <p>{error}</p>
        </section>
      )}

      {analysis && (
        <section>
          <h2>Analysis Output</h2>
          <pre>{JSON.stringify(analysis, null, 2)}</pre>
        </section>
      )}
    </main>
  );
}
