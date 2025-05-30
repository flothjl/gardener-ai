import React from "react";
import { type Garden } from "../types/growkit";
import { Card, CardContent } from "@/components/ui/card";

export default function ValidationCard({ garden }: { garden: Garden }) {
  // For demo, always all clear. For real, display garden.validation/issues.
  // If you get validation issues from agent, show them here.
  const validationIssues =
    (garden.metadata && garden.metadata.validation_issues) || [];

  return (
    <Card className="shadow border border-green-300">
      <CardContent className="py-3 px-4 flex items-center gap-3">
        <span className="font-semibold">Validation:</span>
        {validationIssues.length === 0 ? (
          <span className="text-green-700 font-medium">
            All clear — no conflicts or errors detected.
          </span>
        ) : (
          <ul className="list-disc pl-5 text-red-700 text-sm">
            {validationIssues.map((issue: string, i: number) => (
              <li key={i}>{issue}</li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
