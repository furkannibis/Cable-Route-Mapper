// src/api/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export type AttachmentMapItem = {
  line_number: number;
  cable_type: number;        // 24 / 288
  jacket_type: string;       // "LSZH" | "PE"
  km_int: number;
  km: string;
};


export type AttachmentDetail = {
  line_number: number;
  km: number;
  decreasing_pulley_number: string | null;
  increasing_pulley_number: string | null;
};

export type PulleyDetail = {
  pulley_number: string;
  cable_type: string;
  core: number;
  total_length: number;
  used_length: number;
  remaining_length_calculated: number;
  pulley_last_position: string | null;
  pulley_last_km: string | null;
};

export async function getAttachmentMap(): Promise<AttachmentMapItem[]> {
  const res = await fetch(`${API_BASE}/data/map`);
  if (!res.ok) throw new Error("Map verisi alınamadı");
  return res.json();
}

export async function postAttachment(
  lineNumber: number,
  cableType: number,
  km: number
): Promise<AttachmentDetail> {
  const url = new URL(`${API_BASE}/data/attachment`);
  url.searchParams.set("line_number", String(lineNumber));
  url.searchParams.set("cable_type", String(cableType));
  url.searchParams.set("km", String(km));

  const res = await fetch(url.toString(), { method: "POST" });
  if (!res.ok) throw new Error("Ek noktası sorgusu başarısız");
  return res.json();
}

export async function postPulley(pulleyNumber: string): Promise<PulleyDetail> {
  const url = new URL(`${API_BASE}/data/pulley`);
  url.searchParams.set("pulley_number", pulleyNumber);

  const res = await fetch(url.toString(), { method: "POST" });
  if (!res.ok) throw new Error("Pulley sorgusu başarısız");
  return res.json();
}

export type SegmentDetail = {
  line_number: number;
  cable_type: number;
  start_km: number;
  end_km: number;
  pulleys: string[];
  rows: any[];
};

export async function postSegment(
  lineNumber: number,
  cableType: number,
  startKm: number,
  endKm: number
): Promise<SegmentDetail> {
  const url = new URL(`${API_BASE}/data/segment`);
  url.searchParams.set("line_number", String(lineNumber));
  url.searchParams.set("cable_type", String(cableType));
  url.searchParams.set("start_km", String(startKm));
  url.searchParams.set("end_km", String(endKm));

  const res = await fetch(url.toString(), { method: "POST" });
  if (!res.ok) throw new Error("Segment sorgusu başarısız");
  return res.json();
}
