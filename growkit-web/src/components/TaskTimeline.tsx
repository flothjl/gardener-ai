import React from "react";
import type { GardenTask, Bed } from "../types/growkit";
import { Card, CardContent } from "@/components/ui/card";
import { CalendarCheck2 } from "lucide-react";

function formatDate(d: string) {
  return new Date(d).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function TaskTimeline({
  tasks,
  beds,
}: {
  tasks: GardenTask[];
  beds: Bed[];
}) {
  const sortedTasks = [...tasks].sort((a, b) =>
    a.target_date.localeCompare(b.target_date),
  );

  function bedName(bed_id?: string | null) {
    if (!bed_id) return null;
    const bed = beds.find((b) => b.id === bed_id);
    return bed ? bed.name : null;
  }

  return (
    <Card className="lg:w-1/3 mb-2">
      <CardContent className="p-4">
        <div className="flex items-center gap-2 mb-2">
          <CalendarCheck2 className="text-blue-600 w-5 h-5" />
          <h2 className="text-base font-semibold">Task Timeline</h2>
        </div>
        <ol className="relative border-l border-blue-200 pl-4 mt-4">
          {sortedTasks.map((task) => (
            <li key={task.id} className="mb-8 ml-2">
              <div className="absolute w-3 h-3 bg-blue-200 rounded-full -left-1.5 border border-blue-300" />
              <time className="block mb-1 text-xs text-blue-800 font-semibold">
                {formatDate(task.target_date)}
              </time>
              <span className="font-medium">{task.title}</span>
              {task.related_bed_id && (
                <span className="ml-2 text-xs text-gray-500">
                  ({bedName(task.related_bed_id)})
                </span>
              )}
              {task.completed_on && (
                <span className="ml-2 text-green-700 text-xs">Completed</span>
              )}
            </li>
          ))}
        </ol>
      </CardContent>
    </Card>
  );
}
