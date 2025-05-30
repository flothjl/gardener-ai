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

export default function TaskList({
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
    <Card className="flex-1">
      <CardContent className="p-4">
        <h2 className="text-base font-semibold mb-3 flex items-center gap-2">
          <CalendarCheck2 className="w-5 h-5 text-blue-600" />
          Tasks
        </h2>
        <div className="space-y-3">
          {sortedTasks.map((task) => (
            <Card
              key={task.id}
              className="border bg-slate-50 flex items-center gap-4 px-4 py-2"
            >
              <div>
                <div className="font-semibold">{task.title}</div>
                {task.description && (
                  <div className="text-xs">{task.description}</div>
                )}
                <div className="text-xs text-gray-500">
                  Due: {formatDate(task.target_date)}
                  {task.related_bed_id && (
                    <span className="ml-2">
                      ({bedName(task.related_bed_id)})
                    </span>
                  )}
                  {task.completed_on && (
                    <span className="ml-2 text-green-600">
                      Completed: {formatDate(task.completed_on)}
                    </span>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
