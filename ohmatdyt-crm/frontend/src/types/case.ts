/**
 * Case Types
 * Ohmatdyt CRM - Типи для звернень
 */

// ==================== Статуси звернень ====================

export enum CaseStatus {
  NEW = 'NEW',
  IN_PROGRESS = 'IN_PROGRESS',
  NEEDS_INFO = 'NEEDS_INFO',
  REJECTED = 'REJECTED',
  DONE = 'DONE',
}

export const statusLabels: Record<CaseStatus, string> = {
  NEW: 'Новий',
  IN_PROGRESS: 'В роботі',
  NEEDS_INFO: 'Потрібна інформація',
  REJECTED: 'Відхилено',
  DONE: 'Виконано',
};

export const statusColors: Record<CaseStatus, string> = {
  NEW: 'blue',
  IN_PROGRESS: 'orange',
  NEEDS_INFO: 'red',
  REJECTED: 'red',
  DONE: 'green',
};

// ==================== Базові типи ====================

export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: 'OPERATOR' | 'EXECUTOR' | 'ADMIN';
  is_active?: boolean;
}

export interface Category {
  id: string;
  name: string;
  description?: string;
  is_active?: boolean;
}

export interface Channel {
  id: string;
  name: string;
  description?: string;
  is_active?: boolean;
}

// ==================== Історія статусів ====================

export interface StatusHistory {
  id: string;
  old_status: CaseStatus | null;
  new_status: CaseStatus;
  changed_at: string;
  changed_by: User;
  comment?: string;
}

// ==================== Коментарі ====================

export interface Comment {
  id: string;
  text: string;
  is_internal: boolean;
  created_at: string;
  author: User;
}

// ==================== Вкладення ====================

export interface Attachment {
  id: string;
  file_path: string;
  original_name: string;
  size_bytes: number;
  mime_type: string;
  created_at: string;
  uploaded_by: User;
}

// ==================== Звернення ====================

export interface Case {
  id: string;
  public_id: number;
  category: Category;
  channel: Channel;
  subcategory?: string;
  applicant_name: string;
  applicant_phone?: string;
  applicant_email?: string;
  summary: string;
  status: CaseStatus;
  author: User;
  responsible?: User;
  created_at: string;
  updated_at: string;
}

export interface CaseDetail extends Case {
  status_history: StatusHistory[];
  comments: Comment[];
  attachments: Attachment[];
}

// ==================== Request/Response типи ====================

// FE-011: Запит на редагування полів звернення (ADMIN only)
export interface CaseUpdateRequest {
  category_id?: string;
  channel_id?: string;
  subcategory?: string;
  applicant_name?: string;
  applicant_phone?: string;
  applicant_email?: string;
  summary?: string;
}

// FE-011: Запит на призначення виконавця (ADMIN only)
export interface CaseAssignmentRequest {
  assigned_to_id: string | null; // null = зняти виконавця
}

// Запит на зміну статусу
export interface CaseStatusChangeRequest {
  to_status: CaseStatus;
  comment: string;
}

// Запит на створення коментаря
export interface CreateCommentRequest {
  text: string;
  is_internal: boolean;
}

// Список звернень
export interface CaseListResponse {
  cases: Case[];
  total: number;
  page: number;
  page_size: number;
}

// Список користувачів (для вибору виконавців)
export interface UserListResponse {
  users: User[];
  total: number;
  page: number;
  page_size: number;
}
