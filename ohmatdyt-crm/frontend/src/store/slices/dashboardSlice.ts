/**
 * Dashboard Redux Slice
 * Ohmatdyt CRM - FE-301
 * 
 * State management для дашборду адміністратора
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import api from '@/lib/api';
import {
  DashboardSummary,
  StatusDistribution,
  OverdueCases,
  ExecutorEfficiency,
  CategoriesTop,
  DateRangeFilter,
} from '@/types/dashboard';

// ==================== State Interface ====================

interface DashboardState {
  // Data
  summary: DashboardSummary | null;
  statusDistribution: StatusDistribution | null;
  overdueCases: OverdueCases | null;
  executorEfficiency: ExecutorEfficiency | null;
  categoriesTop: CategoriesTop | null;

  // Loading states
  summaryLoading: boolean;
  statusDistributionLoading: boolean;
  overdueCasesLoading: boolean;
  executorEfficiencyLoading: boolean;
  categoriesTopLoading: boolean;

  // Error states
  summaryError: string | null;
  statusDistributionError: string | null;
  overdueCasesError: string | null;
  executorEfficiencyError: string | null;
  categoriesTopError: string | null;

  // Filters
  dateRange: DateRangeFilter;
  topCategoriesLimit: number;
}

const initialState: DashboardState = {
  summary: null,
  statusDistribution: null,
  overdueCases: null,
  executorEfficiency: null,
  categoriesTop: null,

  summaryLoading: false,
  statusDistributionLoading: false,
  overdueCasesLoading: false,
  executorEfficiencyLoading: false,
  categoriesTopLoading: false,

  summaryError: null,
  statusDistributionError: null,
  overdueCasesError: null,
  executorEfficiencyError: null,
  categoriesTopError: null,

  dateRange: {
    date_from: null,
    date_to: null,
  },
  topCategoriesLimit: 5,
};

// ==================== Async Thunks ====================

/**
 * Отримати загальну статистику дашборду
 */
export const fetchDashboardSummary = createAsyncThunk(
  'dashboard/fetchSummary',
  async (dateRange: DateRangeFilter | undefined, { rejectWithValue }) => {
    try {
      const params: any = {};
      if (dateRange?.date_from) params.date_from = dateRange.date_from;
      if (dateRange?.date_to) params.date_to = dateRange.date_to;

      const response = await api.get<DashboardSummary>('/api/dashboard/summary', { params });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.detail || 'Помилка завантаження статистики'
      );
    }
  }
);

/**
 * Отримати розподіл звернень по статусах
 */
export const fetchStatusDistribution = createAsyncThunk(
  'dashboard/fetchStatusDistribution',
  async (dateRange: DateRangeFilter | undefined, { rejectWithValue }) => {
    try {
      const params: any = {};
      if (dateRange?.date_from) params.date_from = dateRange.date_from;
      if (dateRange?.date_to) params.date_to = dateRange.date_to;

      const response = await api.get<StatusDistribution>('/api/dashboard/status-distribution', { params });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.detail || 'Помилка завантаження розподілу статусів'
      );
    }
  }
);

/**
 * Отримати список прострочених звернень
 */
export const fetchOverdueCases = createAsyncThunk(
  'dashboard/fetchOverdueCases',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get<OverdueCases>('/api/dashboard/overdue-cases');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.detail || 'Помилка завантаження прострочених звернень'
      );
    }
  }
);

/**
 * Отримати статистику ефективності виконавців
 */
export const fetchExecutorEfficiency = createAsyncThunk(
  'dashboard/fetchExecutorEfficiency',
  async (dateRange: DateRangeFilter | undefined, { rejectWithValue }) => {
    try {
      const params: any = {};
      if (dateRange?.date_from) params.date_from = dateRange.date_from;
      if (dateRange?.date_to) params.date_to = dateRange.date_to;

      const response = await api.get<ExecutorEfficiency>('/api/dashboard/executors-efficiency', { params });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.detail || 'Помилка завантаження ефективності виконавців'
      );
    }
  }
);

/**
 * Отримати топ категорій по кількості звернень
 */
export const fetchCategoriesTop = createAsyncThunk(
  'dashboard/fetchCategoriesTop',
  async (
    params: { dateRange?: DateRangeFilter; limit?: number },
    { rejectWithValue }
  ) => {
    try {
      const queryParams: any = {};
      if (params.dateRange?.date_from) queryParams.date_from = params.dateRange.date_from;
      if (params.dateRange?.date_to) queryParams.date_to = params.dateRange.date_to;
      if (params.limit) queryParams.limit = params.limit;

      const response = await api.get<CategoriesTop>('/api/dashboard/categories-top', {
        params: queryParams,
      });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.detail || 'Помилка завантаження топ категорій'
      );
    }
  }
);

/**
 * Завантажити всі дані дашборду одночасно
 */
export const fetchAllDashboardData = createAsyncThunk(
  'dashboard/fetchAllData',
  async (
    params: { dateRange?: DateRangeFilter; limit?: number },
    { dispatch, rejectWithValue }
  ) => {
    try {
      await Promise.all([
        dispatch(fetchDashboardSummary(params.dateRange)),
        dispatch(fetchStatusDistribution(params.dateRange)),
        dispatch(fetchOverdueCases()),
        dispatch(fetchExecutorEfficiency(params.dateRange)),
        dispatch(fetchCategoriesTop({ dateRange: params.dateRange, limit: params.limit })),
      ]);
      return true;
    } catch (error: any) {
      return rejectWithValue('Помилка завантаження даних дашборду');
    }
  }
);

// ==================== Slice ====================

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {
    setDateRange: (state, action: PayloadAction<DateRangeFilter>) => {
      state.dateRange = action.payload;
    },
    setTopCategoriesLimit: (state, action: PayloadAction<number>) => {
      state.topCategoriesLimit = action.payload;
    },
    clearDashboardData: (state) => {
      state.summary = null;
      state.statusDistribution = null;
      state.overdueCases = null;
      state.executorEfficiency = null;
      state.categoriesTop = null;
    },
    clearDashboardErrors: (state) => {
      state.summaryError = null;
      state.statusDistributionError = null;
      state.overdueCasesError = null;
      state.executorEfficiencyError = null;
      state.categoriesTopError = null;
    },
  },
  extraReducers: (builder) => {
    // ==================== Summary ====================
    builder
      .addCase(fetchDashboardSummary.pending, (state) => {
        state.summaryLoading = true;
        state.summaryError = null;
      })
      .addCase(fetchDashboardSummary.fulfilled, (state, action) => {
        state.summaryLoading = false;
        state.summary = action.payload;
      })
      .addCase(fetchDashboardSummary.rejected, (state, action) => {
        state.summaryLoading = false;
        state.summaryError = action.payload as string;
      });

    // ==================== Status Distribution ====================
    builder
      .addCase(fetchStatusDistribution.pending, (state) => {
        state.statusDistributionLoading = true;
        state.statusDistributionError = null;
      })
      .addCase(fetchStatusDistribution.fulfilled, (state, action) => {
        state.statusDistributionLoading = false;
        state.statusDistribution = action.payload;
      })
      .addCase(fetchStatusDistribution.rejected, (state, action) => {
        state.statusDistributionLoading = false;
        state.statusDistributionError = action.payload as string;
      });

    // ==================== Overdue Cases ====================
    builder
      .addCase(fetchOverdueCases.pending, (state) => {
        state.overdueCasesLoading = true;
        state.overdueCasesError = null;
      })
      .addCase(fetchOverdueCases.fulfilled, (state, action) => {
        state.overdueCasesLoading = false;
        state.overdueCases = action.payload;
      })
      .addCase(fetchOverdueCases.rejected, (state, action) => {
        state.overdueCasesLoading = false;
        state.overdueCasesError = action.payload as string;
      });

    // ==================== Executor Efficiency ====================
    builder
      .addCase(fetchExecutorEfficiency.pending, (state) => {
        state.executorEfficiencyLoading = true;
        state.executorEfficiencyError = null;
      })
      .addCase(fetchExecutorEfficiency.fulfilled, (state, action) => {
        state.executorEfficiencyLoading = false;
        state.executorEfficiency = action.payload;
      })
      .addCase(fetchExecutorEfficiency.rejected, (state, action) => {
        state.executorEfficiencyLoading = false;
        state.executorEfficiencyError = action.payload as string;
      });

    // ==================== Categories Top ====================
    builder
      .addCase(fetchCategoriesTop.pending, (state) => {
        state.categoriesTopLoading = true;
        state.categoriesTopError = null;
      })
      .addCase(fetchCategoriesTop.fulfilled, (state, action) => {
        state.categoriesTopLoading = false;
        state.categoriesTop = action.payload;
      })
      .addCase(fetchCategoriesTop.rejected, (state, action) => {
        state.categoriesTopLoading = false;
        state.categoriesTopError = action.payload as string;
      });
  },
});

// ==================== Actions ====================

export const {
  setDateRange,
  setTopCategoriesLimit,
  clearDashboardData,
  clearDashboardErrors,
} = dashboardSlice.actions;

// ==================== Selectors ====================

export const selectDashboardSummary = (state: any) => state.dashboard.summary;
export const selectStatusDistribution = (state: any) => state.dashboard.statusDistribution;
export const selectOverdueCases = (state: any) => state.dashboard.overdueCases;
export const selectExecutorEfficiency = (state: any) => state.dashboard.executorEfficiency;
export const selectCategoriesTop = (state: any) => state.dashboard.categoriesTop;

export const selectSummaryLoading = (state: any) => state.dashboard.summaryLoading;
export const selectStatusDistributionLoading = (state: any) => state.dashboard.statusDistributionLoading;
export const selectOverdueCasesLoading = (state: any) => state.dashboard.overdueCasesLoading;
export const selectExecutorEfficiencyLoading = (state: any) => state.dashboard.executorEfficiencyLoading;
export const selectCategoriesTopLoading = (state: any) => state.dashboard.categoriesTopLoading;

export const selectSummaryError = (state: any) => state.dashboard.summaryError;
export const selectStatusDistributionError = (state: any) => state.dashboard.statusDistributionError;
export const selectOverdueCasesError = (state: any) => state.dashboard.overdueCasesError;
export const selectExecutorEfficiencyError = (state: any) => state.dashboard.executorEfficiencyError;
export const selectCategoriesTopError = (state: any) => state.dashboard.categoriesTopError;

export const selectDateRange = (state: any) => state.dashboard.dateRange;
export const selectTopCategoriesLimit = (state: any) => state.dashboard.topCategoriesLimit;

export default dashboardSlice.reducer;
