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
