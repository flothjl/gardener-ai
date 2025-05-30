import React from "react";
import { type Garden } from "../types/growkit";
import { Card, CardContent } from "@/components/ui/card";

export default function AgentInsights({ garden }: { garden: Garden }) {
  // Pull reasoning from garden.metadata.agent_plan or build a nice message
  const agentPlan =
    garden.metadata?.agent_plan ||
    "This plan optimizes sunlight and companion planting. Tomatoes and basil are paired; salad greens and roots are in separate beds for soil health. Spacing is chosen to avoid crowding.";

  return (
    <Card className="shadow bg-gradient-to-br from-lime-100 to-green-50">
      <CardContent className="py-3 px-4">
        <h3 className="font-semibold mb-1">Agent Insights</h3>
        <p className="text-sm text-gray-700">{agentPlan}</p>
      </CardContent>
    </Card>
  );
}
