export type ActType = 'ACT_1_NORMAL' | 'ACT_2_FIRE' | 'ACT_3_BLOCKAGE';

export interface SiteCoords {
  x: number;
  y: number;
  z?: number;
}

export interface SiteNode {
  id: string;
  name: string;
  zone_type: 'corridor' | 'work_zone' | 'core_tube' | 'core_shaft' | 'hazard_storage' | 'safe_exit' | 'refuge_platform' | 'stair';
  coords: SiteCoords;
  is_exit?: boolean;
}

export interface SiteEdge {
  id: string;
  from_node: string;
  to_node: string;
  distance_m: number;
  width_m: number;
  fire_risk: number;
  smoke_risk: number;
  is_blocked: boolean;
}

export interface WorkerInfo {
  id: string;
  name: string;
  role: string;
  current_node: string;
  status: 'normal' | 'evacuating' | 'trapped' | 'safe';
  heart_rate: number;
  device: string;
}

export interface ScientificMetrics {
  path_efficiency: number;
  static_shortest_m: number;
  max_cost: number;
  avg_cost: number;
  inflexion_points: number;
  speed_reduction_ratio: number;
}

export interface ScientificEvaluation {
  methodology_reference: string;
  algorithm: string;
  fire_stage: string;
  stage_name: string;
  dynamic_weights: {
    temp: number;
    visibility: number;
    co: number;
    alpha?: number;
  };
  replan_latency_ms: number;
  mean_path_efficiency: number;
  max_passage_cost: number;
  mean_passage_cost: number;
  total_inflexion_points: number;
  exit_utilization: Record<string, string>;
}

export interface EvacuationRoute {
  worker_id: string;
  worker_name: string;
  worker_role: string;
  status: 'ROUTE_READY' | 'TRAPPED_NO_PATH' | 'NORMAL_STANDBY';
  target_exit: string;
  exit_name: string;
  path: string[];
  edge_ids: string[];
  distance_m: number;
  est_time_sec: number;
  scientific_metrics?: ScientificMetrics;
}

export interface WorkerBroadcast {
  worker_id: string;
  worker_name: string;
  worker_role: string;
  dialect: 'hunan' | 'sichuan' | 'mandarin';
  device: string;
  alert_level: 'INFO' | 'URGENT' | 'CRITICAL';
  audio_script: string;
  audio_url?: string;
  target_exit: string;
}

export interface PerceptionResult {
  fire_detected: boolean;
  smoke_detected: boolean;
  confidence: number;
  hazard_level: string;
  structural_obstacle: boolean;
  image_url?: string;
  camera_id?: string;
  affected_zone?: string;
  agent_perception_summary: string;
}

export interface ComplianceAudit {
  compliance_status: 'COMPLIANT' | 'WARNING' | 'VIOLATION';
  dual_exit_compliant: boolean;
  max_evac_distance_m: number;
  min_passage_width_m: number;
  audit_notes: string[];
}

export interface IncidentLogItem {
  sequence_id?: number;
  timestamp: string;
  time_offset?: string;
  phase?: 'SENSING' | 'PERCEPTION' | 'ISOLATION' | 'PLANNING' | 'DISPATCH' | 'RESCUE' | 'AUDIT' | string;
  phase_name?: string;
  event_type: string;
  level?: 'INFO' | 'WARNING' | 'CRITICAL' | 'SUCCESS';
  title?: string;
  message: string;
  details?: Record<string, any>;
}

export interface SensorItem {
  id: string;
  name: string;
  type: 'smoke' | 'temp_c' | 'flame' | 'width_m' | 'co_ppm' | string;
  node_id: string;
  node_name: string;
  current_value: number;
  value?: number;
  ppm?: number;
  unit: string;
  threshold: number;
  threshold_operator: '>' | '<';
  status: 'NORMAL' | 'WARNING' | 'ALARM' | 'BLOCKED';
  status_text: string;
  icon: string;
  coords?: { x: number; y: number };
}

export interface ProjectMeta {
  project_name: string;
  floor_level: string;
  standard_applied: string;
}

export interface EmergencyStateResponse {
  project_meta: ProjectMeta;
  current_act: ActType;
  nodes: SiteNode[];
  edges: SiteEdge[];
  workers: WorkerInfo[];
  sensors: SensorItem[];
  plan: {
    routes: EvacuationRoute[];
    compliance_audit: ComplianceAudit;
    scientific_evaluation?: ScientificEvaluation;
    algorithm?: string;
  };
  perception: PerceptionResult;
  broadcasts: WorkerBroadcast[];
  incident_log: IncidentLogItem[];
}
