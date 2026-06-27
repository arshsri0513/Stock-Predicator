"use client";

import { useEffect, useRef, useState } from "react";
import type { OHLCVRow } from "@/lib/types";

/**
 * Candlestick chart -- third approach, after two failed attempts using
 * Recharts' machinery (documented in git history / prior versions of this
 * file for anyone reading later). Both previous versions relied on
 * Recharts internals (a custom Bar `shape` reading `yAxis.scale`, then
 * raw SVG inside `ResponsiveContainer`) that turned out not to provide
 * what their respective approaches needed, rendering nothing.
 *
 * This version drops Recharts ENTIRELY for this one component. We measure
 * our own container's width with a ResizeObserver (a standard browser
 * API, not a charting library internal) and compute every coordinate
 * ourselves in plain numbers -- no percentage strings, no calc(), no
 * library-provided scale functions. This is more code, but every piece
 * of it is something we control and can verify directly, rather than
 * depending on how a third-party library's internals happen to behave.
 */

interface CandlestickChartProps {
  data: OHLCVRow[];
}

const HEIGHT = 300;
const PADDING = { top: 20, bottom: 30, left: 55, right: 15 };

export default function CandlestickChart({ data }: CandlestickChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(0);

  useEffect(() => {
    if (!containerRef.current) return;
    const observer = new ResizeObserver((entries) => {
      setWidth(entries[0].contentRect.width);
    });
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  if (data.length === 0) {
    return null;
  }

  const plotWidth = Math.max(width - PADDING.left - PADDING.right, 0);
  const plotHeight = HEIGHT - PADDING.top - PADDING.bottom;

  const maxPrice = Math.max(...data.map((d) => d.High));
  const minPrice = Math.min(...data.map((d) => d.Low));
  const priceRange = maxPrice - minPrice || 1;

  function priceToY(price: number): number {
    return PADDING.top + plotHeight * (1 - (price - minPrice) / priceRange);
  }

  const slotWidth = plotWidth / data.length;
  const candleBodyWidth = Math.max(Math.min(slotWidth * 0.6, 12), 1);

  const priceTicks = [0, 0.25, 0.5, 0.75, 1].map((frac) => minPrice + priceRange * frac);
  const dateTickEvery = Math.max(Math.ceil(data.length / 8), 1);

  return (
    <div
      className="rounded-lg border p-4"
      style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border-subtle)" }}
    >
      <div ref={containerRef} style={{ width: "100%" }}>
        {width > 0 && (
          <svg width={width} height={HEIGHT}>
            {/* Gridlines + price labels */}
            {priceTicks.map((price, i) => {
              const y = priceToY(price);
              return (
                <g key={i}>
                  <line
                    x1={PADDING.left}
                    x2={width - PADDING.right}
                    y1={y}
                    y2={y}
                    stroke="var(--border-subtle)"
                    strokeDasharray="3 3"
                  />
                  <text x={0} y={y + 4} fontSize={11} fill="var(--text-secondary)">
                    ${price.toFixed(0)}
                  </text>
                </g>
              );
            })}

            {/* Candles */}
            {data.map((row, i) => {
              const cx = PADDING.left + slotWidth * i + slotWidth / 2;
              const isUp = row.Close >= row.Open;
              const color = isUp ? "var(--signal-up)" : "var(--signal-down)";

              const yHigh = priceToY(row.High);
              const yLow = priceToY(row.Low);
              const yOpen = priceToY(row.Open);
              const yClose = priceToY(row.Close);
              const bodyTop = Math.min(yOpen, yClose);
              const bodyHeight = Math.max(Math.abs(yClose - yOpen), 1.5);

              return (
                <g key={i}>
                  <line x1={cx} x2={cx} y1={yHigh} y2={yLow} stroke={color} strokeWidth={1} />
                  <rect
                    x={cx - candleBodyWidth / 2}
                    y={bodyTop}
                    width={candleBodyWidth}
                    height={bodyHeight}
                    fill={color}
                  />
                </g>
              );
            })}

            {/* Date labels */}
            {data.map((row, i) => {
              if (i % dateTickEvery !== 0) return null;
              const cx = PADDING.left + slotWidth * i + slotWidth / 2;
              return (
                <text
                  key={i}
                  x={cx}
                  y={HEIGHT - 8}
                  fontSize={11}
                  fill="var(--text-secondary)"
                  textAnchor="middle"
                >
                  {row.Date.slice(5)}
                </text>
              );
            })}
          </svg>
        )}
      </div>
    </div>
  );
}


