// Admin panel types

export interface AdminQuestion {
  id: number;
  text_en: string;
  text_ar: string | null;
  trait_id: number;
  reverse_scored: boolean;
  order_index: number;
  created_at: string;
}

export interface AdminQuestionCreate {
  text_en: string;
  text_ar?: string | null;
  trait_id: number;
  reverse_scored: boolean;
  order_index: number;
}

export interface AdminQuestionUpdate {
  text_en?: string;
  text_ar?: string | null;
  trait_id?: number;
  reverse_scored?: boolean;
  order_index?: number;
}

export interface AdminIdol {
  id: number;
  name_en: string;
  name_ar: string | null;
  description_en: string | null;
  description_ar: string | null;
  image_url: string | null;
  trait_scores: Record<string, number>;
  created_at: string;
}

export interface AdminIdolCreate {
  name_en: string;
  name_ar?: string | null;
  description_en?: string | null;
  description_ar?: string | null;
  image_url?: string | null;
  trait_scores: Record<string, number>;
}

export interface AdminIdolUpdate {
  name_en?: string;
  name_ar?: string | null;
  description_en?: string | null;
  description_ar?: string | null;
  image_url?: string | null;
  trait_scores?: Record<string, number>;
}

export interface AdminTrait {
  id: number;
  name_en: string;
  name_ar: string | null;
  description_en: string;
  description_ar: string | null;
  high_behavior_en: string | null;
  high_behavior_ar: string | null;
  low_behavior_en: string | null;
  low_behavior_ar: string | null;
  created_at: string;
}

export interface AdminTraitCreate {
  name_en: string;
  name_ar?: string | null;
  description_en: string;
  description_ar?: string | null;
  high_behavior_en?: string | null;
  high_behavior_ar?: string | null;
  low_behavior_en?: string | null;
  low_behavior_ar?: string | null;
}

export interface AdminTraitUpdate {
  name_en?: string;
  name_ar?: string | null;
  description_en?: string;
  description_ar?: string | null;
  high_behavior_en?: string | null;
  high_behavior_ar?: string | null;
  low_behavior_en?: string | null;
  low_behavior_ar?: string | null;
}

export interface AdminStats {
  total_questions: number;
  total_idols: number;
  total_traits: number;
  total_users: number;
  total_tests_completed: number;
  questions_with_arabic: number;
  idols_with_arabic: number;
  traits_with_arabic: number;
}
