const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const API_SECRET_KEY = process.env.NEXT_PUBLIC_API_SECRET_KEY ?? "";

export interface PredictRequest {
  categories: string[];
  mechanics: string[];
}

export interface PredictResponse {
  predicted_rating: number;
}

export async function predictRating(
  payload: PredictRequest
): Promise<PredictResponse> {
  const res = await fetch(`${API_URL}/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_SECRET_KEY,
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "Unknown error");
    throw new Error(`API error ${res.status}: ${text}`);
  }

  return res.json() as Promise<PredictResponse>;
}
