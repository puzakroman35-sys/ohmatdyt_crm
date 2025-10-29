/**
 * Dashboard API Types
 * Ohmatdyt CRM - FE-301
 * 
 * Типи для дашборду адміністратора з аналітикою та статистикою
 */

import { CaseStatus } from '@/store/slices/casesSlice';

// ==================== Dashboard Summary ====================

export interface DashboardSummary {
  total_cases: number;
  new_cases: number;
  in_progress_cases: number;
  needs_info_cases: number;
  rejected_cases: number;
  done_cases: number;
  period_start?: string | null;
  period_end?: string | null;
}

// ==================== Status Distribution ====================

export interface StatusDistributionItem {
  status: CaseStatus;
  count: number;
  percentage: number;
}

export interface StatusDistribution {
  total_cases: number;
  distribution: StatusDistributionItem[];
  period_start?: string | null;
  period_end?: string | null;
}

// ==================== Overdue Cases ====================

export interface OverdueCaseItem {
  id: string;
  public_id: number;
  category_name: string;
  applicant_name: string;
  created_at: string;
  days_overdue: number;
  responsible_id?: string | null;
  responsible_name?: string | null;
}

export interface OverdueCases {
  total_overdue: number;
  cases: OverdueCaseItem[];
}

// ==================== Executor Efficiency ====================

export interface ExecutorEfficiencyItem {
  user_id: string;
  full_name: string;
  email: string;
  categories: string[];
  current_in_progress: number;
  completed_in_period: number;
  avg_completion_days: number | null;
  overdue_count: number;
}

export interface ExecutorEfficiency {
  period_start?: string | null;
  period_end?: string | null;
  executors: ExecutorEfficiencyItem[];
}

// ==================== Top Categories ====================

export interface CategoryTopItem {
  category_id: string;
  category_name: string;
  total_cases: number;
  new_cases: number;
  in_progress_cases: number;
  completed_cases: number;
  percentage_of_total: number;
}

export interface CategoriesTop {
  period_start?: string | null;
  period_end?: string | null;
  total_cases_all_categories: number;
  top_categories: CategoryTopItem[];
  limit: number;
}

// ==================== Date Range Filter ====================

export interface DateRangeFilter {
  date_from?: string | null;
  date_to?: string | null;
}
