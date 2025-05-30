export type UnitLength = "m" | "ft" | "in";

export type Dimensions = {
  width: number;
  length: number;
  depth?: number | null;
  unit?: UnitLength; // default: 'm'
};

export type Coordinates = {
  latitude: number;
  longitude: number;
};

export type Planting = {
  id: string;
  species: string;
  variety?: string | null;
  planted_on?: string | null;
  expected_harvest?: string | null;
  position: [number, number];
  spacing?: number | null;
  notes?: string | null;
  metadata?: Record<string, any> | null;
};

export type Bed = {
  id: string;
  name: string;
  position?: [number, number] | null;
  dimensions: Dimensions;
  soil_type?: string | null;
  plantings: Planting[];
  metadata?: Record<string, any> | null;
};

export type TaskStatus = "pending" | "completed" | "skipped";

export type GardenTask = {
  id: string;
  title: string;
  description?: string | null;
  target_date: string; // ISO date string
  completed_on?: string | null;
  status?: TaskStatus;
  related_planting_id?: string | null;
  related_bed_id?: string | null;
};

export type Garden = {
  schema_version?: string;
  id: string;
  name: string;
  location?: Coordinates | null;
  beds: Bed[];
  tasks: GardenTask[];
  created_at: string; // ISO date-time
  average_last_frost?: string | null;
  average_first_frost?: string | null;
  metadata?: Record<string, any> | null;
};
