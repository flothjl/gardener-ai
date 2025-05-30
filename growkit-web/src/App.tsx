import { useState, useEffect } from "react";
import { type Garden } from "./types/growkit";
import AgentInsights from "./components/AgentInsights";
import ValidationCard from "./components/ValidationCard";
import GardenLayout from "./components/GardenLayout";
import TaskTimeline from "./components/TaskTimeline";
import TaskList from "./components/TaskList";
import { Leaf } from "lucide-react";
import {
  NavigationMenu,
  NavigationMenuList,
  NavigationMenuItem,
} from "@/components/ui/navigation-menu";
import pako from "pako";

function base64UrlToUint8Array(base64: string): Uint8Array {
  base64 = base64.replace(/-/g, "+").replace(/_/g, "/");
  while (base64.length % 4) base64 += "=";
  const raw = atob(base64);
  const arr = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; ++i) arr[i] = raw.charCodeAt(i);
  return arr;
}

function decodeGardenFromQuery(): Garden | null {
  const params = new URLSearchParams(window.location.search);
  const data = params.get("data");
  if (!data) return null;
  try {
    const bytes = base64UrlToUint8Array(data);
    const decompressed = pako.inflate(bytes, { to: "string" });
    return JSON.parse(decompressed);
  } catch (e) {
    console.error("Failed to decode garden from URL:", e);
    return null;
  }
}

export default function App() {
  const [view, setView] = useState<"garden" | "tasks">("garden");
  const [garden, setGarden] = useState<Garden | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      const g = decodeGardenFromQuery();
      if (g && typeof g === "object" && g.name) {
        setGarden(g);
      } else {
        setError("No valid garden data found in URL.");
      }
    } catch {
      setError("An error occurred while loading the garden.");
    }
  }, []);

  if (error || !garden) {
    return (
      <div className="min-h-screen flex flex-col justify-center items-center bg-gradient-to-br from-green-50 to-teal-100">
        <Leaf className="w-12 h-12 mb-2 text-green-500" />
        <h1 className="text-2xl font-bold mb-2">Gardener-AI Viewer</h1>
        <div className="bg-white rounded-lg px-6 py-4 shadow text-center max-w-lg">
          <p className="text-lg font-medium text-red-600 mb-2">
            {error ? error : "No garden data found."}
          </p>
          <p className="text-gray-700 mb-4">
            This page expects a compressed garden definition in the{" "}
            <code className="bg-slate-100 px-1 rounded text-sm">?data=</code>{" "}
            URL parameter.
            <br />
            You can ask the AI assistant to generate a visualization link for
            your garden plan, or paste a valid link here.
          </p>
          <p className="text-xs text-gray-500">
            (Tip: If you are an agent user, try asking:{" "}
            <span className="italic">
              "Show me a link to view this garden."
            </span>
            )
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-teal-100 flex flex-col">
      {/* Header */}
      <header className="flex items-center gap-4 px-8 py-4 shadow bg-white/80 sticky top-0 z-10">
        <Leaf className="text-green-600" />
        <h1 className="text-2xl font-bold tracking-tight">Gardener-AI</h1>
        <span className="text-xs ml-2 bg-green-200 text-green-900 rounded-full px-2 py-0.5">
          {garden.name}
        </span>
        <NavigationMenu>
          <NavigationMenuList>
            <NavigationMenuItem>
              <button
                className={`px-3 py-1 rounded ${view === "garden" ? "bg-green-500 text-white" : "hover:bg-green-200"}`}
                onClick={() => setView("garden")}
              >
                Garden
              </button>
            </NavigationMenuItem>
            <NavigationMenuItem>
              <button
                className={`px-3 py-1 rounded ${view === "tasks" ? "bg-green-500 text-white" : "hover:bg-green-200"}`}
                onClick={() => setView("tasks")}
              >
                Tasks
              </button>
            </NavigationMenuItem>
          </NavigationMenuList>
        </NavigationMenu>
      </header>

      <main className="flex-1 flex flex-col items-center gap-6 p-6">
        <div className="w-full max-w-4xl flex flex-col gap-3">
          <AgentInsights garden={garden} />
          <ValidationCard garden={garden} />
        </div>
        {view === "garden" && <GardenLayout garden={garden} />}
        {view === "tasks" && (
          <div className="flex flex-col lg:flex-row gap-6 w-full max-w-5xl">
            <TaskTimeline tasks={garden.tasks} beds={garden.beds} />
            <TaskList tasks={garden.tasks} beds={garden.beds} />
          </div>
        )}
      </main>
    </div>
  );
}
