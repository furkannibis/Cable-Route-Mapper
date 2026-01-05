"use client";

import { useEffect, useMemo, useState } from "react";

/* ============================================================================
   TYPES & HELPERS
   ==========================================================================*/

const BASE_URL = "http://127.0.0.1:8000";

type Mode = "fiber24" | "fiber288" | "energy";
type LineKey = "L1" | "L2";

type RawCableInfo = {
  "Cable Type": string;
  "Cable Number": string;
  "Cable Core Number"?: number | null;
  "Cable Sheat Type": string;
  "Cable Lenght": number;
  "Cable Remain Lenght": number;
  "Cable Used Lenght": number;
  "Cable Last Location"?: string | null;
};

type RawSpliceItem = {
  "Splice KM": number;
  "Splice Lower Information": RawCableInfo | null;
  "Splice Higher Information": RawCableInfo | null;
};

type CableSheath = "LSZH" | "PE" | "Energy";

type CableInfo = {
  type: string;
  number: string;
  core: number | null;
  sheath: CableSheath;
  length: number;
  remain: number;
  used: number;
  lastLocation: string | null;
};

type Segment = {
  id: string;
  line: LineKey;
  fromKm: number;
  toKm: number;
  cable: CableInfo;
};

type SplicePoint = {
  line: LineKey;
  km: number;
};

type LineData = {
  line: LineKey;
  splices: SplicePoint[];
  segments: Segment[];
};

type MapData = {
  L1: LineData | null;
  L2: LineData | null;
};

type Selected =
  | {
      kind: "splice";
      line: LineKey;
      splice: SplicePoint;
      segmentsAt: Segment[];
    }
  | {
      kind: "segment";
      line: LineKey;
      segment: Segment;
    };

/** 52822 -> "52+822" */
function formatKm(km: number): string {
  const kmPart = Math.floor(km / 1000);
  const mPart = km % 1000;
  return `${kmPart}+${mPart.toString().padStart(3, "0")}`;
}

/** kılıf tipini normalize et */
function normalizeSheath(raw: string, mode: Mode): CableSheath {
  if (mode === "energy") return "Energy";
  const up = raw.toUpperCase();
  if (up.includes("LSZH") || up.includes("A-DQ")) return "LSZH";
  return "PE";
}

function normalizeCable(info: RawCableInfo, mode: Mode): CableInfo {
  return {
    type: info["Cable Type"],
    number: info["Cable Number"],
    core:
      info["Cable Core Number"] === undefined
        ? null
        : (info["Cable Core Number"] as number),
    sheath: normalizeSheath(info["Cable Sheat Type"], mode),
    length: info["Cable Lenght"],
    remain: info["Cable Remain Lenght"],
    used: info["Cable Used Lenght"],
    lastLocation: info["Cable Last Location"] ?? null,
  };
}

/** splice listesinden hat verisi üret */
function buildLineData(
  raw: RawSpliceItem[],
  line: LineKey,
  mode: Mode
): LineData {
  const sorted = [...raw].sort(
    (a, b) => a["Splice KM"] - b["Splice KM"]
  );

  const splices: SplicePoint[] = sorted.map((r) => ({
    line,
    km: r["Splice KM"],
  }));

  const segments: Segment[] = [];

  for (let i = 0; i < sorted.length - 1; i++) {
    const cur = sorted[i];
    const next = sorted[i + 1];

    const fromKm = cur["Splice KM"];
    const toKm = next["Splice KM"];

    const infoUp = cur["Splice Higher Information"];
    const infoDown = next["Splice Lower Information"];
    const chosen = infoUp ?? infoDown;
    if (!chosen) continue;

    const cable = normalizeCable(chosen, mode);

    segments.push({
      id: `${line}-${fromKm}-${toKm}-${cable.number}`,
      line,
      fromKm,
      toKm,
      cable,
    });
  }

  return { line, splices, segments };
}

async function fetchLine(url: string): Promise<RawSpliceItem[]> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

function urlsForMode(mode: Mode): { L1: string; L2: string } {
  switch (mode) {
    case "fiber24":
      return { L1: `${BASE_URL}/fiber/241`, L2: `${BASE_URL}/fiber/242` };
    case "fiber288":
      return { L1: `${BASE_URL}/fiber/2881`, L2: `${BASE_URL}/fiber/2882` };
    case "energy":
      return { L1: `${BASE_URL}/energy/1`, L2: `${BASE_URL}/energy/2` };
  }
}

/* ============================================================================
   MAIN PAGE
   ==========================================================================*/

export default function Page() {
  const [mode, setMode] = useState<Mode>("energy");
  const [mapData, setMapData] = useState<MapData>({ L1: null, L2: null });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [zoom, setZoom] = useState(150); // %
  const [selected, setSelected] = useState<Selected | null>(null);

  // Mode değişince veriyi çek
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        setLoading(true);
        setError(null);

        const urls = urlsForMode(mode);
        const [rawL1, rawL2] = await Promise.all([
          fetchLine(urls.L1),
          fetchLine(urls.L2),
        ]);

        if (cancelled) return;

        const L1 = rawL1.length ? buildLineData(rawL1, "L1", mode) : null;
        const L2 = rawL2.length ? buildLineData(rawL2, "L2", mode) : null;

        setMapData({ L1, L2 });
        setSelected(null);
      } catch (e: any) {
        if (!cancelled) setError(e.message ?? "Veri alınamadı.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [mode]);

  // min / max KM
  const { minKm, maxKm } = useMemo(() => {
    const kms: number[] = [];
    (["L1", "L2"] as LineKey[]).forEach((key) => {
      const d = mapData[key];
      d?.splices.forEach((s) => kms.push(s.km));
    });
    if (!kms.length) return { minKm: 0, maxKm: 1 };
    return { minKm: Math.min(...kms), maxKm: Math.max(...kms) };
  }, [mapData]);

  const pxPerUnit = 0.06 * (zoom / 100);
  const verticalPadding = 40;
  const totalHeight =
    (maxKm - minKm) * pxPerUnit + verticalPadding * 2 || 300;

  const activeLabel =
    mode === "fiber24" ? "Fiber 24C" : mode === "fiber288" ? "Fiber 288C" : "Energy";

  const handleSpliceClick = (line: LineKey, km: number) => {
    const lineData = mapData[line];
    if (!lineData) return;

    const splice: SplicePoint = { line, km };
    const segmentsAt = lineData.segments.filter(
      (s) => s.fromKm === km || s.toKm === km
    );

    setSelected({
      kind: "splice",
      line,
      splice,
      segmentsAt,
    });
  };

  const handleSegmentClick = (line: LineKey, seg: Segment) => {
    setSelected({ kind: "segment", line, segment: seg });
  };

  return (
    <>
      <main className="min-h-screen w-full bg-slate-100 text-slate-900 flex">
        {/* SIDEBAR */}
        <aside className="w-64 border-r border-slate-200 bg-white flex flex-col">
          <div className="p-4 pb-2 border-b border-slate-100">
            <h1 className="text-lg font-semibold leading-tight">
              Fiber / Energy Deployment
            </h1>
            <p className="mt-1 text-[11px] text-slate-500">
              24 / 288 core fiber ve enerji kablolarının ek noktaları ve
              aradaki kablo çekimleri.
            </p>
            <p className="mt-1 text-[11px]">
              <span className="text-slate-500">Aktif: </span>
              <span className="font-semibold">{activeLabel}</span>
            </p>
          </div>

          <div className="p-4 pt-3 space-y-4 text-[11px]">
            {/* MODE */}
            <div>
              <div className="mb-1 font-semibold">Katman</div>
              <div className="flex flex-col gap-1">
                <button
                  onClick={() => setMode("fiber24")}
                  className={`px-3 py-1 rounded-md border text-left ${
                    mode === "fiber24"
                      ? "bg-slate-900 text-white border-slate-900"
                      : "bg-white hover:bg-slate-50 border-slate-200"
                  }`}
                >
                  Fiber 24C
                </button>
                <button
                  onClick={() => setMode("fiber288")}
                  className={`px-3 py-1 rounded-md border text-left ${
                    mode === "fiber288"
                      ? "bg-slate-900 text-white border-slate-900"
                      : "bg-white hover:bg-slate-50 border-slate-200"
                  }`}
                >
                  Fiber 288C
                </button>
                <button
                  onClick={() => setMode("energy")}
                  className={`px-3 py-1 rounded-md border text-left ${
                    mode === "energy"
                      ? "bg-slate-900 text-white border-slate-900"
                      : "bg-white hover:bg-slate-50 border-slate-200"
                  }`}
                >
                  Energy
                </button>
              </div>
            </div>

            {/* ZOOM */}
            <div>
              <div className="mb-1 font-semibold flex items-center justify-between">
                <span>Zoom</span>
                <span className="text-[10px] text-slate-500">
                  {zoom}
                  {"%"}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  className="h-6 w-6 rounded-full border border-slate-300 flex items-center justify-center text-xs"
                  onClick={() =>
                    setZoom((z) =>
                      Math.max(60, Math.round((z - 20) / 10) * 10)
                    )
                  }
                >
                  -
                </button>
                <input
                  type="range"
                  min={60}
                  max={300}
                  step={10}
                  value={zoom}
                  onChange={(e) => setZoom(Number(e.target.value))}
                  className="flex-1"
                />
                <button
                  className="h-6 w-6 rounded-full border border-slate-300 flex items-center justify-center text-xs"
                  onClick={() =>
                    setZoom((z) =>
                      Math.min(300, Math.round((z + 20) / 10) * 10)
                    )
                  }
                >
                  +
                </button>
              </div>
            </div>

            {/* LEGEND */}
            <div>
              <div className="mb-1 font-semibold">Tipler</div>
              <div className="flex flex-col gap-1">
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-emerald-500" />
                  <span>LSZH</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-orange-500" />
                  <span>PE</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="h-[2px] w-4 bg-slate-500" />
                  <span>Hat</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-slate-800" />
                  <span>Ek noktası</span>
                </div>
              </div>
            </div>

            <p className="text-[10px] text-slate-500 pt-2 border-t border-slate-200">
              Detay görmek için sağdaki haritada bir ek noktasına veya kablo
              segmentine tıklayın. Detaylar popup olarak açılır.
            </p>
          </div>
        </aside>

        {/* MAP AREA */}
        <section className="flex-1 p-6 overflow-auto">
          <div className="flex flex-col gap-4">
            <div className="flex items-baseline justify-between">
              <h2 className="text-sm font-semibold">Harita</h2>
              {loading && (
                <span className="text-[11px] text-slate-500">
                  Yükleniyor...
                </span>
              )}
              {error && (
                <span className="text-[11px] text-red-600">
                  Hata: {error}
                </span>
              )}
            </div>

            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-4 overflow-auto">
              <div
                className="flex gap-16 relative"
                style={{ height: totalHeight }}
              >
                {/* KM skalası (yukarı büyük, aşağı küçük) */}
                <KmAxis
                  minKm={minKm}
                  maxKm={maxKm}
                  pxPerUnit={pxPerUnit}
                  verticalPadding={verticalPadding}
                />

                {/* Line 1 & Line 2 */}
                <div className="flex-1 flex justify-center gap-40">
                  <LineColumn
                    label="Hat 1"
                    lineKey="L1"
                    data={mapData.L1}
                    minKm={minKm}
                    maxKm={maxKm}
                    pxPerUnit={pxPerUnit}
                    verticalPadding={verticalPadding}
                    onSpliceClick={handleSpliceClick}
                    onSegmentClick={handleSegmentClick}
                  />
                  <LineColumn
                    label="Hat 2"
                    lineKey="L2"
                    data={mapData.L2}
                    minKm={minKm}
                    maxKm={maxKm}
                    pxPerUnit={pxPerUnit}
                    verticalPadding={verticalPadding}
                    onSpliceClick={handleSpliceClick}
                    onSegmentClick={handleSegmentClick}
                  />
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* POPUP / MODAL */}
      {selected && (
        <Modal onClose={() => setSelected(null)}>
          <DetailContent selected={selected} />
        </Modal>
      )}
    </>
  );
}

/* ============================================================================
   KM AXIS
   ==========================================================================*/

function KmAxis({
  minKm,
  maxKm,
  pxPerUnit,
  verticalPadding,
}: {
  minKm: number;
  maxKm: number;
  pxPerUnit: number;
  verticalPadding: number;
}) {
  if (maxKm <= minKm) return null;

  const range = maxKm - minKm;
  const approxTicks = 8;
  const rawStep = range / approxTicks;

  const base = 500; // 0.5 km
  const step = Math.max(base, Math.round(rawStep / base) * base);

  const ticks: number[] = [];
  for (let km = maxKm; km >= minKm; km -= step) {
    ticks.push(km);
  }

  return (
    <div className="w-16 relative text-[10px] text-slate-700">
      {ticks.map((km) => {
        const y = (maxKm - km) * pxPerUnit + verticalPadding;
        return (
          <div
            key={km}
            className="absolute left-0 -translate-y-1/2 flex items-center gap-1"
            style={{ top: y }}
          >
            <span className="text-right w-10">{formatKm(km)}</span>
            <span className="h-[1px] flex-1 bg-slate-300" />
          </div>
        );
      })}
    </div>
  );
}

/* ============================================================================
   LINE COLUMN (HATLAR)
   ==========================================================================*/

interface LineColumnProps {
  label: string;
  lineKey: LineKey;
  data: LineData | null;
  minKm: number;
  maxKm: number;
  pxPerUnit: number;
  verticalPadding: number;
  onSpliceClick: (line: LineKey, km: number) => void;
  onSegmentClick: (line: LineKey, seg: Segment) => void;
}

function LineColumn({
  label,
  lineKey,
  data,
  minKm,
  maxKm,
  pxPerUnit,
  verticalPadding,
  onSpliceClick,
  onSegmentClick,
}: LineColumnProps) {
  return (
    <div className="flex flex-col items-center text-[11px]">
      <div className="mb-2 font-semibold">{label}</div>
      <div className="relative w-32 h-full flex items-stretch justify-center">
        {/* Arka plan capsule */}
        <div className="absolute left-1/2 -translate-x-1/2 top-0 bottom-0 w-20 rounded-full bg-slate-100" />

        {/* Ana hat */}
        <div className="absolute left-1/2 -translate-x-1/2 top-4 bottom-4 w-[3px] bg-slate-500 rounded-full" />

        {/* Segmentler */}
        {data &&
          data.segments.map((seg) => {
            const topPx =
              (maxKm - seg.toKm) * pxPerUnit + verticalPadding;
            const bottomPx =
              (maxKm - seg.fromKm) * pxPerUnit + verticalPadding;
            const height = Math.max(8, bottomPx - topPx);

            const colorClass =
              seg.cable.sheath === "LSZH"
                ? "bg-emerald-500"
                : seg.cable.sheath === "PE"
                ? "bg-orange-500"
                : "bg-blue-500";

            return (
              <button
                key={seg.id}
                type="button"
                className="absolute left-1/2 -translate-x-1/2 w-6 rounded-full shadow-sm hover:shadow-md transition-shadow border border-slate-200 flex flex-col items-center justify-center bg-white/70"
                style={{ top: topPx, height }}
                onClick={() => onSegmentClick(lineKey, seg)}
              >
                <div
                  className={`w-[12px] rounded-full ${colorClass}`}
                  style={{ height: height - 4 }}
                />
                <span className="absolute left-7 text-[9px] text-slate-700 whitespace-nowrap">
                  {seg.cable.number}
                </span>
              </button>
            );
          })}

        {/* Ek noktaları */}
        {data &&
          data.splices.map((sp, idx) => {
            const y =
              (maxKm - sp.km) * pxPerUnit + verticalPadding;
            return (
              <button
                key={`${sp.km}-${idx}`}
                type="button"
                className="absolute left-1/2 -translate-x-1/2 -translate-y-1/2 h-2 w-2 rounded-full bg-slate-800 border border-slate-50 hover:scale-110 transition-transform"
                style={{ top: y }}
                onClick={() => onSpliceClick(lineKey, sp.km)}
                title={formatKm(sp.km)}
              />
            );
          })}
      </div>
    </div>
  );
}

/* ============================================================================
   MODAL & DETAIL CONTENT
   ==========================================================================*/

function Modal({
  children,
  onClose,
}: {
  children: React.ReactNode;
  onClose: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* arka plan */}
      <div
        className="absolute inset-0 bg-black/40"
        onClick={onClose}
      />
      {/* içerik */}
      <div className="relative bg-white rounded-2xl shadow-xl max-w-xl w-full mx-4 p-4 border border-slate-200">
        <button
          type="button"
          className="absolute right-3 top-3 h-6 w-6 rounded-full border border-slate-300 flex items-center justify-center text-xs text-slate-600 hover:bg-slate-100"
          onClick={onClose}
        >
          ✕
        </button>
        {children}
      </div>
    </div>
  );
}

function DetailContent({ selected }: { selected: Selected }) {
  if (selected.kind === "segment") {
    const { segment, line } = selected;
    const c = segment.cable;

    return (
      <div className="text-[11px] space-y-1 pr-4 text-black">
        <h3 className="text-sm font-semibold mb-2">
          Kablo Segmenti – {line === "L1" ? "Line 1" : "Line 2"}
        </h3>
        <div>
          <span className="font-medium">KM Aralığı:</span>{" "}
          {formatKm(segment.fromKm)} – {formatKm(segment.toKm)}
        </div>
        <div>
          <span className="font-medium">Cable Number:</span> {c.number}
        </div>
        <div>
          <span className="font-medium">Type:</span> {c.type}
        </div>
        {c.core !== null && (
          <div>
            <span className="font-medium">Core:</span> {c.core}
          </div>
        )}
        <div>
          <span className="font-medium">Sheath:</span> {c.sheath}
        </div>
        <div>
          <span className="font-medium">Lenght:</span> {c.length} m
        </div>
        <div>
          <span className="font-medium">Used:</span> {c.used} m
        </div>
        <div>
          <span className="font-medium">Remain:</span> {c.remain} m
        </div>
        {c.lastLocation && (
          <div>
            <span className="font-medium">Last Location:</span>{" "}
            {c.lastLocation}
          </div>
        )}
      </div>
    );
  }

  const { splice, line, segmentsAt } = selected;
  const incoming = segmentsAt.filter((s) => s.toKm === splice.km);
  const outgoing = segmentsAt.filter((s) => s.fromKm === splice.km);

  return (
    <div className="text-[11px] space-y-2 pr-4 text-black">
      <h3 className="text-sm font-semibold mb-2">
        Ek Noktası – {line === "L1" ? "Line 1" : "Line 2"}
      </h3>
      <div>
        <span className="font-medium">KM:</span> {formatKm(splice.km)}
      </div>

      {incoming.length === 0 && outgoing.length === 0 && (
        <p className="text-[10px] text-slate-500">
          Bu ek noktasına bağlı kablo segmenti bulunamadı.
        </p>
      )}

      {incoming.length > 0 && (
        <div>
          <div className="font-medium text-[11px] mb-1">
            Azalan (gelen) kablo(lar)
          </div>
          {incoming.map((seg) => (
            <SpliceCableInfo key={seg.id} seg={seg} />
          ))}
        </div>
      )}

      {outgoing.length > 0 && (
        <div>
          <div className="font-medium text-[11px] mb-1">
            Artan (giden) kablo(lar)
          </div>
          {outgoing.map((seg) => (
            <SpliceCableInfo key={seg.id} seg={seg} />
          ))}
        </div>
      )}
    </div>
  );
}

function SpliceCableInfo({ seg }: { seg: Segment }) {
  const c = seg.cable;
  return (
    <div className="border border-slate-200 rounded-md p-1.5 mb-1 space-y-0.5 text-[10px]">
      <div>
        <span className="font-medium">KM Aralığı:</span>{" "}
        {formatKm(seg.fromKm)} – {formatKm(seg.toKm)}
      </div>
      <div>
        <span className="font-medium">Cable Number:</span> {c.number}
      </div>
      <div>
        <span className="font-medium">Type:</span> {c.type}
      </div>
      {c.core !== null && (
        <div>
          <span className="font-medium">Core:</span> {c.core}
        </div>
      )}
      <div>
        <span className="font-medium">Sheath:</span> {c.sheath}
      </div>
      <div>
        <span className="font-medium">Lenght:</span> {c.length} m
      </div>
      <div>
        <span className="font-medium">Used:</span> {c.used} m
      </div>
      <div>
        <span className="font-medium">Remain:</span> {c.remain} m
      </div>
      {c.lastLocation && (
        <div>
          <span className="font-medium">Last Location:</span>{" "}
          {c.lastLocation}
        </div>
      )}
    </div>
  );
}
