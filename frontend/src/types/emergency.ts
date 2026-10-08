export type ActType = 'ACT_1_NORMAL' | 'ACT_2_FIRE' | 'ACT_3_BLOCKAGE';

export interface SiteCoords {
  x: number;
  y: number;
  z?: number;
}

export interface SiteNode {
  id: string;
  name: string;
  zone_type: 'corridor' | 'work_zone' | 'core_tube' | 'safe_exit' | 'refuge_platform' | 'stair';
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
  timestamp: string;
  event_type: string;
  message: string;
  details?: Record<string, any>;
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
  sensors: any[];
  plan: {
    routes: EvacuationRoute[];
    compliance_audit: ComplianceAudit;
    algorithm: string;
  };
  perception: PerceptionResult;
  broadcasts: WorkerBroadcast[];
  incident_log: IncidentLogItem[];
}
