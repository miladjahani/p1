export interface RecoveryInput {
  flow_rate: number;
  acid_conc: number;
  time_days: number;
  ore_grade: number;
  particle_size?: number;
}

export interface RecoveryOutput {
  recovery_percent: number;
  calculation_method: string;
}

export interface OPEXInput {
  tonnage: number;
  days: number;
  acid_price?: number;
  labor_cost?: number;
  diesel_price?: number;
}

export interface OPEXOutput {
  acid_consumption_kg: number;
  acid_cost_usd: number;
  labor_cost_usd: number;
  diesel_cost_usd: number;
  overhead_usd: number;
  total_opex_usd: number;
  opex_per_ton_usd: number;
}

export interface PLSInput {
  flow_rate: number;
  area: number;
  recovery: number;
  ore_grade: number;
  tonnage: number;
}

export interface PLSOutput {
  total_flow_m3_day: number;
  copper_dissolved_kg_year: number;
  cu_concentration_g_L: number;
  target_ph: number;
  annual_cathode_tonnes: number;
}

export interface MonthlySchedule {
  month: number;
  cathode_tonnes: number;
  ore_processed_tonnes: number;
}

export interface ScheduleInput {
  target_cathode: number;
  ore_grade: number;
  recovery: number;
  days?: number;
}

export interface ScheduleOutput {
  required_ore_tonnes: number;
  daily_feed_tonnes: number;
  monthly_schedule: MonthlySchedule[];
  target_achieved: boolean;
}

export interface PadVolumeInput {
  L: number;
  W: number;
  H_top: number;
  H_bottom: number;
  slope_deg: number;
  terrain_slope_x?: number;
  terrain_slope_y?: number;
}

export interface PadVolumeOutput {
  volume_m3: number;
  tonnage: number;
  density_t_m3: number;
  surface_area_m2: number;
  avg_height_m: number;
}

export interface AcidOptimizationInput {
  pls_flow: number;
  cu_conc: number;
  target_ph: number;
  current_ph: number;
}

export interface AcidOptimizationOutput {
  acid_kg_per_hour: number;
  acid_tonnes_per_day: number;
  ph_adjustment: number;
  recommendation: string;
}

export interface HeapPad {
  id: number;
  name?: string;
  L: number;
  W: number;
  H: number;
  x: number;
  z: number;
  slope_deg: number;
  bounds?: Record<string, string>;
  lateral_spacing: number;
  emitter_spacing: number;
  emitter_flow_rate: number;
  ore_grade: number;
  recovery: number;
  density: number;
  volume_m3: number;
  tonnage: number;
  recoverable_copper_tonnes: number;
  created_at: string;
  updated_at: string;
}
