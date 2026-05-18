export type ApiMode = 'mock' | 'live';

export interface ApiError {
  code: string;
  message: string;
  details: string[];
}

export interface SOPReviewRequest {
  full_name: string;
  mobile: string;
  university: string;
  intake: string;
  country: string;
  sop_text: string;
}

export interface GatekeeperResponse {
  is_valid: boolean;
  reason: string;
}

export interface CriterionFeedback {
  name:
    | 'Academic Fit'
    | 'University Specificity'
    | 'Career Clarity'
    | 'Narrative Flow'
    | 'Language & Tone';
  score: number;
  feedback: string;
}

export interface SOPGrade {
  overall_score: number;
  criteria_breakdown: CriterionFeedback[];
  summary: string;
}

export interface SOPReviewResponse {
  mode: ApiMode;
  gatekeeper: GatekeeperResponse;
  grade: SOPGrade | null;
}

export interface AdmissionsPredictionRequest {
  full_name: string;
  target_intake: string;
  target_country: string;
  undergrad_degree_name: string;
  cgpa: number;
  cgpa_scale: 4 | 10;
  gre_score: number | null;
  gmat_score: number | null;
  english_test: 'IELTS' | 'TOEFL' | null;
  english_score: number | null;
  work_experience_months: number;
  research_publications: number;
  target_programs: string[];
}

export interface ProgramPrediction {
  program_name: string;
  chance_category: 'Safe' | 'Target' | 'Reach' | 'Unrealistic';
  estimated_probability_percentage: number;
  brief_reasoning: string;
}

export interface AdmissionPrediction {
  target_predictions: ProgramPrediction[];
  profile_strengths: string[];
  profile_weaknesses: string[];
  actionable_roadmap: string[];
  recommended_universities: string[];
}

export interface AdmissionsPredictionResponse {
  mode: ApiMode;
  prediction: AdmissionPrediction;
}
