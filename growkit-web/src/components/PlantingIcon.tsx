import React from "react";
import { Apple, Carrot, Leaf, Sprout, Flower2 } from "lucide-react";

export default function PlantingIcon({ species }: { species: string }) {
  switch (species.toLowerCase()) {
    case "tomato":
      return <Apple className="w-6 h-6 text-red-600" />;
    case "basil":
      return <Sprout className="w-5 h-5 text-green-700" />;
    case "carrot":
      return <Carrot className="w-6 h-6 text-orange-500" />;
    case "lettuce":
      return <Leaf className="w-6 h-6 text-green-500" />;
    case "flower":
      return <Flower2 className="w-6 h-6 text-pink-400" />;
    default:
      return <Sprout className="w-6 h-6 text-gray-400" />;
  }
}
