import React, { useRef, useState } from "react";
import { type Garden } from "../types/growkit";
import { Card, CardContent } from "@/components/ui/card";
import PlantingIcon from "./PlantingIcon";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Compass } from "lucide-react";

const CANVAS_W = 1200;
const CANVAS_H = 900;
const FT_TO_PX = 36;

function getPlantBg(species: string) {
  switch (species.toLowerCase()) {
    case "tomato":
      return "bg-red-100 border-red-400";
    case "basil":
      return "bg-green-100 border-green-400";
    case "carrot":
      return "bg-orange-100 border-orange-400";
    case "lettuce":
      return "bg-green-50 border-green-300";
    case "flower":
      return "bg-pink-100 border-pink-400";
    default:
      return "bg-gray-100 border-gray-300";
  }
}

export default function GardenLayout({ garden }: { garden: Garden }) {
  // Pan and zoom state
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [dragging, setDragging] = useState(false);
  const last = useRef<{ x: number; y: number } | null>(null);

  function onSvgMouseDown(e: React.MouseEvent) {
    setDragging(true);
    last.current = { x: e.clientX, y: e.clientY };
  }
  function onSvgMouseUp() {
    setDragging(false);
    last.current = null;
  }
  function onSvgMouseMove(e: React.MouseEvent) {
    if (!dragging || !last.current) return;
    const dx = e.clientX - last.current.x;
    const dy = e.clientY - last.current.y;
    setPan((prev) => ({ x: prev.x + dx, y: prev.y + dy }));
    last.current = { x: e.clientX, y: e.clientY };
  }
  const handleZoomIn = () => setZoom((z) => Math.min(z + 0.2, 2.5));
  const handleZoomOut = () => setZoom((z) => Math.max(z - 0.2, 0.5));
  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  return (
    <Card className="w-full max-w-5xl shadow-xl border border-green-200">
      <CardContent className="p-4">
        {/* Header with zoom buttons */}
        <div className="flex justify-between items-center mb-2">
          <h2 className="text-xl font-semibold text-green-900">
            Garden Visualization
          </h2>
          <div className="flex items-center gap-2">
            <button
              className="bg-green-100 border border-green-300 rounded-full p-2 hover:bg-green-200 transition shadow"
              onClick={handleZoomIn}
              aria-label="Zoom In"
              type="button"
            >
              +
            </button>
            <button
              className="bg-green-100 border border-green-300 rounded-full p-2 hover:bg-green-200 transition shadow"
              onClick={handleZoomOut}
              aria-label="Zoom Out"
              type="button"
            >
              -
            </button>
            <button
              className="bg-green-50 border border-green-300 rounded-full p-2 hover:bg-green-100 transition shadow"
              onClick={handleReset}
              aria-label="Reset"
              type="button"
            >
              Reset
            </button>
            <span className="ml-2 text-xs text-gray-600">
              Zoom: {(zoom * 100).toFixed(0)}%
            </span>
          </div>
        </div>
        {/* Compass */}
        <div className="relative">
          <div className="absolute left-3 top-3 z-20 flex flex-col items-center pointer-events-none select-none">
            <div className="bg-white/90 rounded-full p-1 border shadow">
              <Compass className="w-7 h-7 text-slate-700" />
            </div>
            <span className="text-xs text-gray-500 font-bold -mt-1">N</span>
          </div>
          {/* Fixed-size, overflow-hidden SVG container */}
          <div
            className="rounded-xl border shadow-inner bg-gradient-to-br from-white via-green-50 to-lime-50 overflow-hidden"
            style={{
              width: 700,
              height: 440,
              cursor: dragging ? "grabbing" : "grab",
              userSelect: "none",
              margin: "0 auto",
              position: "relative",
              boxSizing: "content-box",
            }}
            tabIndex={0}
            onMouseDown={onSvgMouseDown}
            onMouseUp={onSvgMouseUp}
            onMouseLeave={onSvgMouseUp}
            onMouseMove={onSvgMouseMove}
            role="region"
            aria-label="Garden Visualization"
          >
            <svg
              width="100%"
              height="100%"
              viewBox={`0 0 ${CANVAS_W} ${CANVAS_H}`}
              className="block rounded-xl"
              style={{
                width: "100%",
                height: "100%",
                background: "transparent",
                display: "block",
                pointerEvents: "all",
              }}
            >
              <defs>
                <pattern
                  id="smallGrid"
                  width={FT_TO_PX}
                  height={FT_TO_PX}
                  patternUnits="userSpaceOnUse"
                >
                  <path
                    d={`M ${FT_TO_PX} 0 L 0 0 0 ${FT_TO_PX}`}
                    fill="none"
                    stroke="#e5e7eb"
                    strokeWidth="1"
                  />
                </pattern>
                <pattern
                  id="grid"
                  width={FT_TO_PX * 2}
                  height={FT_TO_PX * 2}
                  patternUnits="userSpaceOnUse"
                >
                  <rect
                    width={FT_TO_PX * 2}
                    height={FT_TO_PX * 2}
                    fill="url(#smallGrid)"
                  />
                  <path
                    d={`M ${FT_TO_PX * 2} 0 L 0 0 0 ${FT_TO_PX * 2}`}
                    fill="none"
                    stroke="#b6e3b5"
                    strokeWidth="2"
                  />
                </pattern>
                {/* Gradients for each bed */}
                {garden.beds.map((bed, idx) => (
                  <linearGradient
                    key={bed.id}
                    id={`bed${idx}`}
                    x1="0"
                    y1="0"
                    x2="1"
                    y2="1"
                  >
                    <stop offset="0%" stopColor="#bef264" />
                    <stop offset="100%" stopColor="#5eead4" />
                  </linearGradient>
                ))}
              </defs>
              {/* Grid */}
              <rect width={CANVAS_W} height={CANVAS_H} fill="url(#grid)" />
              {/* Pan/Zoom GROUP */}
              <g
                style={{
                  transform: `translate(${pan.x}px,${pan.y}px) scale(${zoom})`,
                  transformOrigin: "0 0",
                  transition: dragging
                    ? "none"
                    : "transform 0.13s cubic-bezier(.4,2,.7,1)",
                }}
              >
                {/* Beds */}
                {garden.beds.map((bed, idx) => {
                  if (!bed.position) return null;
                  const [x, y] = bed.position;
                  const bx = x * FT_TO_PX;
                  const by = y * FT_TO_PX;
                  const bw = bed.dimensions.width * FT_TO_PX;
                  const bh = bed.dimensions.length * FT_TO_PX;
                  return (
                    <g key={bed.id}>
                      <rect
                        x={bx}
                        y={by}
                        width={bw}
                        height={bh}
                        rx={18}
                        fill={`url(#bed${idx})`}
                        stroke="#15803d"
                        strokeWidth={4}
                        className="transition-all duration-200"
                      />
                      <text
                        x={bx + bw / 2}
                        y={by - 14}
                        textAnchor="middle"
                        className="font-bold text-green-800 text-md"
                        style={{
                          fontSize: 18,
                          paintOrder: "stroke fill",
                          stroke: "white",
                          strokeWidth: 2,
                        }}
                      >
                        {bed.name}
                      </text>
                      {bed.soil_type && (
                        <text
                          x={bx + bw - 10}
                          y={by + 18}
                          textAnchor="end"
                          className="text-xs font-medium"
                          fill="#6d28d9"
                          style={{
                            fontSize: 12,
                            paintOrder: "stroke fill",
                            stroke: "white",
                            strokeWidth: 1,
                          }}
                        >
                          {bed.soil_type}
                        </text>
                      )}
                      {bed.plantings.map((p) => {
                        const [px, py] = p.position;
                        const iconX = bx + px * FT_TO_PX;
                        const iconY = by + py * FT_TO_PX;
                        return (
                          <TooltipProvider key={p.id}>
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <g className="cursor-pointer">
                                  <rect
                                    x={iconX - 16}
                                    y={iconY - 16}
                                    width={32}
                                    height={32}
                                    rx={10}
                                    className={`stroke-1 stroke-gray-200 ${getPlantBg(p.species)} shadow`}
                                  />
                                  <g
                                    transform={`translate(${iconX - 12}, ${iconY - 12})`}
                                  >
                                    <PlantingIcon species={p.species} />
                                  </g>
                                </g>
                              </TooltipTrigger>
                              <TooltipContent>
                                <div className="font-semibold">
                                  {p.species}
                                  {p.variety && ` (${p.variety})`}
                                </div>
                                {p.spacing && (
                                  <div className="text-xs">
                                    Spacing: {p.spacing}ft
                                  </div>
                                )}
                                {p.notes && (
                                  <div className="text-xs">{p.notes}</div>
                                )}
                                {p.planted_on && (
                                  <div className="text-xs text-gray-500">
                                    Planted: {p.planted_on}
                                  </div>
                                )}
                                {p.expected_harvest && (
                                  <div className="text-xs text-gray-500">
                                    Harvest: {p.expected_harvest}
                                  </div>
                                )}
                              </TooltipContent>
                            </Tooltip>
                          </TooltipProvider>
                        );
                      })}
                    </g>
                  );
                })}
              </g>
            </svg>
          </div>
        </div>
        {/* Legend */}
        <div className="flex gap-5 mt-4 items-center text-sm justify-center">
          <span className="font-semibold text-gray-700">Legend:</span>
          <span className="flex items-center gap-1">
            <PlantingIcon species="Tomato" /> Tomato
          </span>
          <span className="flex items-center gap-1">
            <PlantingIcon species="Basil" /> Basil
          </span>
          <span className="flex items-center gap-1">
            <PlantingIcon species="Carrot" /> Carrot
          </span>
          <span className="flex items-center gap-1">
            <PlantingIcon species="Lettuce" /> Lettuce
          </span>
          <span className="flex items-center gap-1">
            <PlantingIcon species="Flower" /> Flower
          </span>
        </div>
        <div className="text-xs text-gray-500 mt-2 flex justify-center">
          <span>Pan: drag canvas &bull; Zoom: use buttons</span>
        </div>
      </CardContent>
    </Card>
  );
}
