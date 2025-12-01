"use client";

import { useEffect, useMemo, useState } from "react";
import {
  getAttachmentMap,
  postAttachment,
  postSegment,
  postPulley,
  AttachmentMapItem,
  AttachmentDetail,
  SegmentDetail,
  PulleyDetail,
} from "@/api/api";

type Segment = {
  line_number: number;
  cable_type: number;
  jacket_type: string | null;
  start_km_int: number;
  end_km_int: number;
  start_km_label: string;
  end_km_label: string;
};

export default function Page() {
  const [mapData, setMapData] = useState<AttachmentMapItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Zoom
  const [zoom, setZoom] = useState(1.0); // 0.5–2.0 arası

  // Ek detayı
  const [attachmentDetail, setAttachmentDetail] = useState<AttachmentDetail | null>(null);
  const [attachmentLoading, setAttachmentLoading] = useState(false);
  const [attachmentError, setAttachmentError] = useState<string | null>(null);

  // Segment detayı
  const [segmentDetail, setSegmentDetail] = useState<SegmentDetail | null>(null);
  const [segmentLoading, setSegmentLoading] = useState(false);
  const [segmentError, setSegmentError] = useState<string | null>(null);

  // Pulley detayı
  const [pulleyDetail, setPulleyDetail] = useState<PulleyDetail | null>(null);
  const [pulleyLoading, setPulleyLoading] = useState(false);
  const [pulleyError, setPulleyError] = useState<string | null>(null);

  // ---------- DATA LOAD ----------
  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const data = await getAttachmentMap();
        setMapData(data);
      } catch (err: any) {
        setError(err.message ?? "Map verisi alınamadı");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // Min / max km
  const [minKm, maxKm] = useMemo(() => {
    if (mapData.length === 0) return [0, 1];
    const kms = mapData.map((m) => m.km_int);
    return [Math.min(...kms), Math.max(...kms)];
  }, [mapData]);

  const range = maxKm - minKm || 1;

  // Line bazlı ayır
  const line1Items = useMemo(
    () => mapData.filter((m) => m.line_number === 1),
    [mapData]
  );
  const line2Items = useMemo(
    () => mapData.filter((m) => m.line_number === 2),
    [mapData]
  );

  // ---------- SEGMENT HESABI ----------
  const buildSegmentsForSet = (items: AttachmentMapItem[]): Segment[] => {
    const segments: Segment[] = [];
    const groups = new Map<string, AttachmentMapItem[]>();

    // line + cable_type + jacket_type ile grupla
    for (const item of items) {
      const key = `${item.line_number}-${item.cable_type}-${item.jacket_type ?? "UNK"}`;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key)!.push(item);
    }

    for (const [, arr] of groups.entries()) {
      const sorted = [...arr].sort((a, b) => a.km_int - b.km_int);

      for (let i = 0; i < sorted.length - 1; i++) {
        const a = sorted[i];
        const b = sorted[i + 1];

        segments.push({
          line_number: a.line_number,
          cable_type: a.cable_type,
          jacket_type: a.jacket_type ?? null,
          start_km_int: a.km_int,
          end_km_int: b.km_int,
          start_km_label: a.km,
          end_km_label: b.km,
        });
      }
    }

    return segments;
  };

  // ---------- CLICK HANDLERS ----------
  const resetDetails = () => {
    setAttachmentDetail(null);
    setAttachmentError(null);
    setAttachmentLoading(false);

    setSegmentDetail(null);
    setSegmentError(null);
    setSegmentLoading(false);

    setPulleyDetail(null);
    setPulleyError(null);
    setPulleyLoading(false);
  };

  const handlePointClick = async (item: AttachmentMapItem) => {
    try {
      resetDetails();
      setAttachmentLoading(true);

      const detail = await postAttachment(item.line_number, item.cable_type, item.km_int);
      setAttachmentDetail(detail);
    } catch (err: any) {
      setAttachmentError(err.message ?? "Ek noktası bilgisi alınamadı");
    } finally {
      setAttachmentLoading(false);
    }
  };

  const handleSegmentClick = async (seg: Segment) => {
    try {
      resetDetails();
      setSegmentLoading(true);

      const detail = await postSegment(
        seg.line_number,
        seg.cable_type,
        seg.start_km_int,
        seg.end_km_int
      );
      setSegmentDetail(detail);
    } catch (err: any) {
      setSegmentError(err.message ?? "Segment bilgisi alınamadı");
    } finally {
      setSegmentLoading(false);
    }
  };

  const handlePulleyClick = async (pulleyNumber: string) => {
    try {
      setPulleyError(null);
      setPulleyDetail(null);
      setPulleyLoading(true);

      const detail = await postPulley(pulleyNumber);
      setPulleyDetail(detail);
    } catch (err: any) {
      setPulleyError(err.message ?? "Makara bilgisi alınamadı");
    } finally {
      setPulleyLoading(false);
    }
  };

  // ---------- RENDER HELPERS ----------
  const renderCapsule = (items: AttachmentMapItem[], segments: Segment[]) => {
    return (
      <div className="relative w-40 h-full rounded-full bg-slate-200 flex items-stretch justify-center overflow-hidden">
        {/* Dikey ana hat – tam ortada */}
        <div className="absolute top-10 bottom-10 left-1/2 -translate-x-1/2 w-[2px] bg-slate-400" />

        {/* Kablo segmentleri (renkli bantlar) */}
        {segments.map((seg, idx) => {
          const y1 = ((seg.start_km_int - minKm) / range) * 100;
          const y2 = ((seg.end_km_int - minKm) / range) * 100;
          const heightPercent = (y2 - y1) * 0.8;
          const mid = ((seg.start_km_int + seg.end_km_int) / 2 - minKm) / range * 100;

          const bgColor =
            seg.jacket_type === "LSZH"
              ? "rgba(16,185,129,0.45)" // yeşil
              : seg.jacket_type === "PE"
              ? "rgba(249,115,22,0.45)" // turuncu
              : "rgba(59,130,246,0.4)";

          const label =
            seg.jacket_type != null
              ? `${seg.cable_type} ${seg.jacket_type}`
              : `${seg.cable_type}`;

          return (
            <div key={`seg-${seg.line_number}-${seg.cable_type}-${seg.start_km_int}-${idx}`}>
              {/* Segment bar – tam merkezde, tıklanabilir */}
              <button
                type="button"
                className="absolute -translate-x-1/2 cursor-pointer group"
                style={{
                  left: "50%",
                  top: `calc(${y1}% * 0.8 + 10%)`,
                  height: `calc(${heightPercent}% )`,
                  width: "10px",
                  borderRadius: "9999px",
                  backgroundColor: bgColor,
                }}
                onClick={() => handleSegmentClick(seg)}
                title={`${seg.start_km_label} – ${seg.end_km_label}`}
              />

              {/* Segment etiketi – barın sağında */}
              {heightPercent > 4 && (
                <div
                  className="absolute -translate-y-1/2 text-[11px] text-slate-800 font-medium whitespace-nowrap"
                  style={{
                    top: `calc(${mid}% * 0.8 + 10%)`,
                    left: "calc(50% + 16px)",
                  }}
                >
                  {label}
                </div>
              )}
            </div>
          );
        })}

        {/* Ek noktaları (tek renk, tam merkezde) + yanında km etiketi */}
        {items.map((item, idx) => {
          const percent = ((item.km_int - minKm) / range) * 100;
          const top = `calc(${percent}% * 0.8 + 10%)`;

          return (
            <div key={item.line_number + "-" + item.cable_type + "-" + item.km_int + "-" + idx}>
              {/* Noktanın kendisi – çizgiyle tam aynı merkezde */}
              <button
                type="button"
                className="absolute -translate-x-1/2 -translate-y-1/2"
                style={{ left: "50%", top }}
                onClick={() => handlePointClick(item)}
              >
                <div className="h-3.5 w-3.5 rounded-full shadow-md bg-slate-700 hover:scale-125 transition-transform" />
              </button>

              {/* Km etiketi – noktanın sağında */}
              <div
                className="absolute -translate-y-1/2 text-[11px] text-slate-800"
                style={{ left: "calc(50% + 12px)", top }}
              >
                {item.km}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const renderLineColumn = (items: AttachmentMapItem[]) => {
    const items24 = items.filter((it) => it.cable_type === 24);
    const items288 = items.filter((it) => it.cable_type === 288);

    const segments24 = buildSegmentsForSet(items24);
    const segments288 = buildSegmentsForSet(items288);

    const baseHeight = 1400; // piksel cinsinden, sonra scale uygulanıyor

    return (
      <div className="flex justify-center">
        {/* zoom uygulanacak alanı saran kutu */}
        <div className="relative max-h-[1400px] overflow-auto">
          <div
            className="relative flex items-stretch gap-8"
            style={{
              height: baseHeight,
              transform: `scale(${zoom})`,
              transformOrigin: "top center",
            }}
          >
            <div className="flex flex-col items-center">
              <span className="text-xs text-slate-600 mb-1">24 core</span>
              {renderCapsule(items24, segments24)}
            </div>
            <div className="flex flex-col items-center">
              <span className="text-xs text-slate-600 mb-1">288 core</span>
              {renderCapsule(items288, segments288)}
            </div>
          </div>
        </div>
      </div>
    );
  };

  // ---------- POPUP ----------
  const isPopupOpen =
    attachmentLoading ||
    attachmentDetail ||
    attachmentError ||
    segmentLoading ||
    segmentDetail ||
    segmentError ||
    pulleyLoading ||
    pulleyDetail ||
    pulleyError;

  const closePopup = () => {
    resetDetails();
  };

  // ---------- RENDER ----------
  return (
    <main className="min-h-screen w-full bg-slate-100 text-slate-900 p-6 flex flex-col gap-6">
      <header>
        <h1 className="text-2xl font-bold mb-1">Fiber Ek Noktası Haritası</h1>
      </header>

      {/* Zoom bar */}
      <div className="mt-1 mb-2 flex items-center gap-3 text-xs text-slate-700">
        <span className="font-medium">Zoom:</span>
        <button
          type="button"
          className="px-2 py-1 rounded border border-slate-300 hover:bg-slate-100"
          onClick={() => setZoom((z) => Math.max(0.5, +(z - 0.1).toFixed(2)))}
        >
          −
        </button>
        <input
          type="range"
          min={0.5}
          max={1}
          step={0.1}
          value={zoom}
          onChange={(e) => setZoom(parseFloat(e.target.value))}
          className="w-40"
        />
        <button
          type="button"
          className="px-2 py-1 rounded border border-slate-300 hover:bg-slate-100"
          onClick={() => setZoom((z) => Math.min(2, +(z + 0.1).toFixed(2)))}
        >
          +
        </button>
        <span className="w-10 text-right tabular-nums">
          {(zoom * 100).toFixed(0)}%
        </span>
      </div>

      <section className="bg-white rounded-2xl shadow p-4 flex-1 flex flex-col gap-6">
        {loading && <p className="text-sm text-slate-500">Yükleniyor...</p>}
        {error && <p className="text-sm text-red-600">{error}</p>}

        {!loading && !error && mapData.length === 0 && (
          <p className="text-sm text-slate-500">Veri bulunamadı.</p>
        )}

        {!loading && !error && mapData.length > 0 && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
              <div>
                <div className="text-sm font-semibold mb-3 text-center">Hat 1</div>
                {renderLineColumn(line1Items)}
              </div>
              <div>
                <div className="text-sm font-semibold mb-3 text-center">Hat 2</div>
                {renderLineColumn(line2Items)}
              </div>
            </div>

            {/* Legend */}
            <div className="flex flex-wrap gap-4 text-xs justify-center mt-2">
              <div className="flex items-center gap-1">
                <span className="inline-block h-3.5 w-3.5 rounded-full bg-slate-700" />
                <span>Ek noktası</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="inline-block h-2 w-6 rounded-full bg-emerald-400" />
                <span>LSZH</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="inline-block h-2 w-6 rounded-full bg-orange-400" />
                <span>PE</span>
              </div>
            </div>
          </>
        )}
      </section>

      {/* POPUP */}
      {isPopupOpen && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-lg p-4 w-full max-w-md text-sm max-h-[90vh] overflow-auto">
            <div className="flex justify-between items-center mb-2">
              <h2 className="font-semibold">
                {segmentDetail
                  ? "Ek Detay"
                  : attachmentDetail
                  ? "Ek Noktası Detayı"
                  : "Detay"}
              </h2>
              <button
                className="text-xs text-slate-500 hover:text-slate-800"
                onClick={closePopup}
              >
                Kapat
              </button>
            </div>

            {/* Ek detayı (segment yoksa) */}
            {!segmentDetail && (
              <>
                {attachmentLoading && (
                  <p className="text-slate-500">Ek bilgisi yükleniyor...</p>
                )}
                {attachmentError && <p className="text-red-600">{attachmentError}</p>}
                {attachmentDetail && (
                  <>
                    <p>
                      <span className="font-medium">Hat:</span>{" "}
                      {attachmentDetail.line_number}
                    </p>
                    <p>
                      <span className="font-medium">Km:</span> {attachmentDetail.km}
                    </p>
                    <p className="mt-2">
                      <span className="font-medium">Azalan Makara:</span>{" "}
                      {attachmentDetail.decreasing_pulley_number ? (
                        <button
                          type="button"
                          className="text-sky-700 underline"
                          onClick={() =>
                            handlePulleyClick(
                              attachmentDetail.decreasing_pulley_number as string
                            )
                          }
                        >
                          {attachmentDetail.decreasing_pulley_number}
                        </button>
                      ) : (
                        "-"
                      )}
                    </p>
                    <p>
                      <span className="font-medium">Artan Makara:</span>{" "}
                      {attachmentDetail.increasing_pulley_number ? (
                        <button
                          type="button"
                          className="text-sky-700 underline"
                          onClick={() =>
                            handlePulleyClick(
                              attachmentDetail.increasing_pulley_number as string
                            )
                          }
                        >
                          {attachmentDetail.increasing_pulley_number}
                        </button>
                      ) : (
                        "-"
                      )}
                    </p>
                  </>
                )}
              </>
            )}

            {/* Segment detayı */}
            {segmentDetail && (
              <>
                {segmentLoading && (
                  <p className="text-slate-500">Segment bilgisi yükleniyor...</p>
                )}
                {segmentError && <p className="text-red-600">{segmentError}</p>}
                {!segmentLoading && !segmentError && (
                  <>
                    <p>
                      <span className="font-medium">Hat:</span>{" "}
                      {segmentDetail.line_number}
                    </p>
                    <p>
                      <span className="font-medium">Core:</span>{" "}
                      {segmentDetail.cable_type}
                    </p>
                    <p>
                      <span className="font-medium">Km Aralığı:</span>{" "}
                      {segmentDetail.start_km} – {segmentDetail.end_km}
                    </p>
                    <p className="mt-2">
                      <span className="font-medium">Makaralar:</span>{" "}
                      {segmentDetail.pulleys.length === 0 && "Yok"}
                    </p>
                    <ul className="list-disc list-inside">
                      {segmentDetail.pulleys.map((p) => (
                        <li key={p}>
                          <button
                            type="button"
                            className="text-sky-700 underline"
                            onClick={() => handlePulleyClick(p)}
                          >
                            {p}
                          </button>
                        </li>
                      ))}
                    </ul>
                  </>
                )}
              </>
            )}

            {/* Pulley detayı */}
            {(pulleyLoading || pulleyDetail || pulleyError) && (
              <div className="mt-4 border-t pt-3">
                <h3 className="font-semibold mb-1 text-sm">Makara Detayı</h3>
                {pulleyLoading && (
                  <p className="text-slate-500">Makara bilgisi yükleniyor...</p>
                )}
                {pulleyError && <p className="text-red-600">{pulleyError}</p>}
                {pulleyDetail && (
                  <div className="space-y-1">
                    <p>
                      <span className="font-medium">Makara:</span>{" "}
                      {pulleyDetail.pulley_number}
                    </p>
                    <p>
                      <span className="font-medium">Tip:</span>{" "}
                      {pulleyDetail.cable_type} / {pulleyDetail.core} core
                    </p>
                    <p>
                      <span className="font-medium">Toplam:</span>{" "}
                      {pulleyDetail.total_length} m
                    </p>
                    <p>
                      <span className="font-medium">Kullanılan:</span>{" "}
                      {pulleyDetail.used_length} m
                    </p>
                    <p>
                      <span className="font-medium">Hesap Kalan:</span>{" "}
                      {pulleyDetail.remaining_length_calculated} m
                    </p>
                    <p>
                      <span className="font-medium">Son Konum:</span>{" "}
                      {pulleyDetail.pulley_last_position ?? "-"}{" "}
                      {pulleyDetail.pulley_last_km
                        ? `(${pulleyDetail.pulley_last_km})`
                        : ""}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </main>
  );
}
