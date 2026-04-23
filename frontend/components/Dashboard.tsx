"use client";

import { useEffect, useState } from "react";

import { getJson, postJson } from "@/lib/api";

type User = { id: number; anonymized_id: string };

type BaselineForm = {
  age: number;
  sex: string;
  height_cm: number;
  weight_kg: number;
  body_fat_pct?: number;
  occupation_type: string;
  medical_conditions: string;
  primary_goal: string;
};

type DailyForm = {
  log_date: string;
  calories?: number;
  protein_g?: number;
  carbs_g?: number;
  fats_g?: number;
  meal_timing: string;
  sleep_hours?: number;
  sleep_quality?: number;
  steps?: number;
  exercise_minutes?: number;
  exercise_type: string;
  sedentary_minutes?: number;
  water_liters?: number;
  stress_level?: number;
  alcohol_units?: number;
  smoking_status: string;
  diet_type: string;
  heart_rate?: number;
  blood_sugar?: number;
  weight_kg?: number;
};

export default function Dashboard() {
  const [email, setEmail] = useState("");
  const [user, setUser] = useState<User | null>(null);
  const [capabilities, setCapabilities] = useState<Record<string, unknown> | null>(null);
  const [analysis, setAnalysis] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [baseline, setBaseline] = useState<BaselineForm>({
    age: 30,
    sex: "female",
    height_cm: 168,
    weight_kg: 65,
    occupation_type: "desk",
    medical_conditions: "",
    primary_goal: "improve sleep and body composition",
  });

  const [daily, setDaily] = useState<DailyForm>({
    log_date: new Date().toISOString().slice(0, 10),
    meal_timing: "regular",
    exercise_type: "strength",
    smoking_status: "non-smoker",
    diet_type: "balanced",
  });

  useEffect(() => {
    getJson<Record<string, unknown>>("/platform/capabilities").then(setCapabilities).catch(() => undefined);
  }, []);

  async function createUser() {
    setError(null);
    try {
      const created = await postJson<User>("/users", { email });
      setUser(created);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Create user failed");
    }
  }

  async function saveBaseline() {
    if (!user) return;
    setError(null);
    try {
      await postJson("/baseline", { user_id: user.id, ...baseline });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Baseline save failed");
    }
  }

  async function saveDailyLog() {
    if (!user) return;
    setError(null);
    try {
      await postJson("/logs", { user_id: user.id, ...daily });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Daily save failed");
    }
  }

  async function runAnalysis() {
    if (!user) return;
    setError(null);
    try {
      const result = await getJson<Record<string, unknown>>(`/users/${user.id}/analysis`);
      setAnalysis(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed");
    }
  }

  return (
    <main>
      <h1>Health Intelligence Platform</h1>
      <p>Backend-first platform: one statistical engine, multiple client interfaces.</p>

      <section>
        <h2>Platform Capabilities</h2>
        <pre>{JSON.stringify(capabilities, null, 2)}</pre>
      </section>

      <section>
        <h2>1) Identity (PII separated in backend)</h2>
        <label>Email<input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="user@example.com" /></label>
        <button onClick={createUser}>Create User</button>
        {user && <p>Anonymized user: <span className="badge">{user.anonymized_id.slice(0, 14)}</span></p>}
      </section>

      <section>
        <h2>2) Baseline Onboarding</h2>
        <div className="grid">
          <label>Age<input type="number" value={baseline.age} onChange={(e) => setBaseline({ ...baseline, age: Number(e.target.value) })} /></label>
          <label>Sex<input value={baseline.sex} onChange={(e) => setBaseline({ ...baseline, sex: e.target.value })} /></label>
          <label>Height cm<input type="number" value={baseline.height_cm} onChange={(e) => setBaseline({ ...baseline, height_cm: Number(e.target.value) })} /></label>
          <label>Weight kg<input type="number" value={baseline.weight_kg} onChange={(e) => setBaseline({ ...baseline, weight_kg: Number(e.target.value) })} /></label>
          <label>Body fat %<input type="number" value={baseline.body_fat_pct ?? ""} onChange={(e) => setBaseline({ ...baseline, body_fat_pct: Number(e.target.value) })} /></label>
          <label>Occupation<input value={baseline.occupation_type} onChange={(e) => setBaseline({ ...baseline, occupation_type: e.target.value })} /></label>
          <label>Medical conditions<input value={baseline.medical_conditions} onChange={(e) => setBaseline({ ...baseline, medical_conditions: e.target.value })} /></label>
          <label>Goal<input value={baseline.primary_goal} onChange={(e) => setBaseline({ ...baseline, primary_goal: e.target.value })} /></label>
        </div>
        <button onClick={saveBaseline} disabled={!user}>Save Baseline</button>
      </section>

      <section>
        <h2>3) Daily Structured Logging</h2>
        <div className="grid">
          <label>Date<input type="date" value={daily.log_date} onChange={(e) => setDaily({ ...daily, log_date: e.target.value })} /></label>
          <label>Calories<input type="number" onChange={(e) => setDaily({ ...daily, calories: Number(e.target.value) })} /></label>
          <label>Protein g<input type="number" onChange={(e) => setDaily({ ...daily, protein_g: Number(e.target.value) })} /></label>
          <label>Carbs g<input type="number" onChange={(e) => setDaily({ ...daily, carbs_g: Number(e.target.value) })} /></label>
          <label>Fats g<input type="number" onChange={(e) => setDaily({ ...daily, fats_g: Number(e.target.value) })} /></label>
          <label>Meal timing<input value={daily.meal_timing} onChange={(e) => setDaily({ ...daily, meal_timing: e.target.value })} /></label>
          <label>Sleep hours<input type="number" step="0.1" onChange={(e) => setDaily({ ...daily, sleep_hours: Number(e.target.value) })} /></label>
          <label>Sleep quality<input type="number" onChange={(e) => setDaily({ ...daily, sleep_quality: Number(e.target.value) })} /></label>
          <label>Steps<input type="number" onChange={(e) => setDaily({ ...daily, steps: Number(e.target.value) })} /></label>
          <label>Exercise min<input type="number" onChange={(e) => setDaily({ ...daily, exercise_minutes: Number(e.target.value) })} /></label>
          <label>Exercise type<input value={daily.exercise_type} onChange={(e) => setDaily({ ...daily, exercise_type: e.target.value })} /></label>
          <label>Sedentary min<input type="number" onChange={(e) => setDaily({ ...daily, sedentary_minutes: Number(e.target.value) })} /></label>
          <label>Water liters<input type="number" step="0.1" onChange={(e) => setDaily({ ...daily, water_liters: Number(e.target.value) })} /></label>
          <label>Stress level<input type="number" onChange={(e) => setDaily({ ...daily, stress_level: Number(e.target.value) })} /></label>
          <label>Alcohol units<input type="number" step="0.1" onChange={(e) => setDaily({ ...daily, alcohol_units: Number(e.target.value) })} /></label>
          <label>Smoking<input value={daily.smoking_status} onChange={(e) => setDaily({ ...daily, smoking_status: e.target.value })} /></label>
          <label>Diet type<input value={daily.diet_type} onChange={(e) => setDaily({ ...daily, diet_type: e.target.value })} /></label>
          <label>Heart rate<input type="number" onChange={(e) => setDaily({ ...daily, heart_rate: Number(e.target.value) })} /></label>
          <label>Blood sugar<input type="number" step="0.1" onChange={(e) => setDaily({ ...daily, blood_sugar: Number(e.target.value) })} /></label>
          <label>Weight kg<input type="number" step="0.1" onChange={(e) => setDaily({ ...daily, weight_kg: Number(e.target.value) })} /></label>
        </div>
        <div className="grid">
          <button onClick={saveDailyLog} disabled={!user}>Save Daily Log</button>
          <button onClick={runAnalysis} disabled={!user}>Run Full SSDI Pipeline</button>
        </div>
      </section>

      {error && <section><strong>Error:</strong> {error}</section>}
      {analysis && <section><h2>4) Statistical Output</h2><pre>{JSON.stringify(analysis, null, 2)}</pre></section>}
    </main>
  );
}
