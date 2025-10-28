/**
 * Cases Slice - Управління станом звернень
 * Ohmatdyt CRM
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

// Типи
export type CaseStatus = 'NEW' | 'IN_PROGRESS' | 'NEEDS_INFO' | 'REJECTED' | 'DONE';

export interface Category {
  id: string;
  name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Channel {
  id: string;
  name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: 'OPERATOR' | 'EXECUTOR' | 'ADMIN';
  is_active: boolean;
}

export interface Case {
  id: string;
  public_id: number;
  category_id: string;
  channel_id: string;
  subcategory?: string;
  applicant_name: string;
  applicant_phone?: string;
  applicant_email?: string;
  summary: string;
  status: CaseStatus;
  author_id: string;
  responsible_id?: string;
  created_at: string;
  updated_at: string;
  category?: Category;
  channel?: Channel;
  author?: User;
  responsible?: User;
}

// Async Thunks
export const fetchCasesAsync = createAsyncThunk(
  'cases/fetchCases',
  async (params: {
    endpoint?: string;
    filters?: Record<string, any>;
    pagination?: { skip: number; limit: number };
    sort?: { field: string; order: 'asc' | 'desc' };
  }, { rejectWithValue }) => {
    try {
      const { endpoint = '/api/cases', filters = {}, pagination = { skip: 0, limit: 50 }, sort } = params;

      const queryParams = new URLSearchParams({
        skip: pagination.skip.toString(),
        limit: pagination.limit.toString(),
      });

      // Додавання фільтрів
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          if (Array.isArray(value)) {
            value.forEach(v => queryParams.append(key, v));
          } else {
            queryParams.append(key, value.toString());
          }
        }
      });

      // Додавання сортування
      if (sort) {
        const orderBy = sort.order === 'desc' ? `-${sort.field}` : sort.field;
        queryParams.append('order_by', orderBy);
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${endpoint}?${queryParams}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

export interface CasesState {
  cases: Case[];
  currentCase: Case | null;
  isLoading: boolean;
  error: string | null;
  total: number;
  page: number;
  pageSize: number;
}

// Початковий стан
const initialState: CasesState = {
  cases: [],
  currentCase: null,
  isLoading: false,
  error: null,
  total: 0,
  page: 1,
  pageSize: 50,
};

// Slice
const casesSlice = createSlice({
  name: 'cases',
  initialState,
  reducers: {
    // Початок завантаження списку звернень
    fetchCasesStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    
    // Успішне завантаження списку
    fetchCasesSuccess: (
      state,
      action: PayloadAction<{
        cases: Case[];
        total: number;
        page: number;
        pageSize: number;
      }>
    ) => {
      state.isLoading = false;
      state.cases = action.payload.cases;
      state.total = action.payload.total;
      state.page = action.payload.page;
      state.pageSize = action.payload.pageSize;
      state.error = null;
    },
    
    // Помилка завантаження
    fetchCasesFailure: (state, action: PayloadAction<string>) => {
      state.isLoading = false;
      state.error = action.payload;
    },
    
    // Завантаження деталей звернення
    fetchCaseStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    
    // Успішне завантаження деталей
    fetchCaseSuccess: (state, action: PayloadAction<Case>) => {
      state.isLoading = false;
      state.currentCase = action.payload;
      state.error = null;
    },
    
    // Помилка завантаження деталей
    fetchCaseFailure: (state, action: PayloadAction<string>) => {
      state.isLoading = false;
      state.error = action.payload;
    },
    
    // Створення нового звернення
    createCaseStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    
    createCaseSuccess: (state, action: PayloadAction<Case>) => {
      state.isLoading = false;
      state.cases.unshift(action.payload);
      state.total += 1;
      state.error = null;
    },
    
    createCaseFailure: (state, action: PayloadAction<string>) => {
      state.isLoading = false;
      state.error = action.payload;
    },
    
    // Оновлення звернення
    updateCaseSuccess: (state, action: PayloadAction<Case>) => {
      const index = state.cases.findIndex((c) => c.id === action.payload.id);
      if (index !== -1) {
        state.cases[index] = action.payload;
      }
      if (state.currentCase?.id === action.payload.id) {
        state.currentCase = action.payload;
      }
    },
    
    // Очистити поточне звернення
    clearCurrentCase: (state) => {
      state.currentCase = null;
    },
    
    // Очистити помилку
    clearError: (state) => {
      state.error = null;
    },
    
    // Скинути стан
    resetCasesState: () => initialState,
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCasesAsync.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchCasesAsync.fulfilled, (state, action) => {
        state.isLoading = false;
        state.cases = action.payload.cases || [];
        state.total = action.payload.total || 0;
        state.error = null;
      })
      .addCase(fetchCasesAsync.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

// Експорт actions
export const {
  fetchCasesStart,
  fetchCasesSuccess,
  fetchCasesFailure,
  fetchCaseStart,
  fetchCaseSuccess,
  fetchCaseFailure,
  createCaseStart,
  createCaseSuccess,
  createCaseFailure,
  updateCaseSuccess,
  clearCurrentCase,
  clearError,
  resetCasesState,
} = casesSlice.actions;

// Селектори
export const selectCases = (state: { cases: CasesState }) => state.cases.cases;
export const selectCurrentCase = (state: { cases: CasesState }) =>
  state.cases.currentCase;
export const selectCasesLoading = (state: { cases: CasesState }) =>
  state.cases.isLoading;
export const selectCasesError = (state: { cases: CasesState }) =>
  state.cases.error;
export const selectCasesTotal = (state: { cases: CasesState }) =>
  state.cases.total;

// Експорт reducer
export default casesSlice.reducer;
