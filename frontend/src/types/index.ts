export interface Question {
  id: number;
  text: string;
  trait_id: number;
  order_index: number;
}

export interface TestStartResponse {
  session_id: string;
  questions: Question[];
  total_questions: number;
}

export interface Answer {
  question_id: number;
  answer: number;
}

export interface TraitScore {
  trait_id: number;
  trait_name: string;
  score: number;
}

export interface IdolMatch {
  idol_id: number;
  name: string;
  description: string | null;
  image_url: string | null;
  similarity: number;
  similarity_percentage: number;
}

export interface ResultResponse {
  result_id: number;
  user_trait_scores: TraitScore[];
  top_matches: IdolMatch[];
  created_at: string;
}

export interface TraitComparison {
  trait_id: number;
  trait_name: string;
  user_score: number;
  idol_score: number;
  difference: number;
}

export interface JourneyScenarioOption {
  option_code: string;
  option_text_en: string;
  option_text_ar: string | null;
}

export interface JourneyScenario {
  scenario_code: string;
  order_index: number;
  scenario_text_en: string;
  scenario_text_ar: string | null;
  options: JourneyScenarioOption[];
}

export interface JourneyStartResponse {
  test_run_id: number;
  version_id: string;
  scenarios: JourneyScenario[];
}

export interface JourneyAnswerSubmission {
  scenario_code: string;
  option_code: string;
}

export interface JourneyTopGene {
  gene_code: string;
  name_en: string;
  name_ar: string | null;
  desc_en: string;
  desc_ar: string | null;
  raw_score: number;
  normalized_score: number;
  rank: number;
  role: string;
}

export interface JourneyArchetypeMatch {
  model_code: string;
  name_en: string;
  name_ar: string | null;
  summary_ar: string | null;
  similarity: number;
  rank: number;
}

export interface JourneyActivationItem {
  channel: string;
  advice_id: string;
  advice_type: string;
  title_en: string;
  title_ar: string | null;
  body_en: string;
  body_ar: string | null;
  priority: number;
}

export interface JourneySubmitAnswersRequest {
  version_id: string;
  test_run_id: number;
  answers: JourneyAnswerSubmission[];
}

export interface JourneySubmitAnswersResponse {
  version_id: string;
  test_run_id: number;
  top_genes: JourneyTopGene[];
  archetype_matches: JourneyArchetypeMatch[];
  activation_items: JourneyActivationItem[];
}

export interface JourneyFeedbackRequest {
  test_run_id: number;
  judged_score: number;
  selected_activation_id?: string;
}

export interface JourneyFeedbackResponse {
  test_run_id: number;
  judged_score: number;
  selected_activation_id: string | null;
  status: string;
}
