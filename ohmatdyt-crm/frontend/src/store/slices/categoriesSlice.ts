/**
 * Categories Redux Slice
 * Ohmatdyt CRM - Управління категоріями
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Типи
export interface Category {
  id: string;
  name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateCategoryData {
  name: string;
}

export interface UpdateCategoryData {
  name: string;
}

export interface CategoriesState {
  categories: Category[];
  total: number;
  currentCategory: Category | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: CategoriesState = {
  categories: [],
  total: 0,
  currentCategory: null,
  isLoading: false,
  error: null,
};

// Async Thunks

/**
 * Отримання списку категорій з фільтрами
 */
export const fetchCategoriesAsync = createAsyncThunk(
  'categories/fetchCategories',
  async (params: {
    skip?: number;
    limit?: number;
    search?: string;
    include_inactive?: boolean;
  } = {}) => {
    const token = localStorage.getItem('access_token');
    const response = await axios.get(`${API_URL}/api/categories`, {
      params,
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  }
);

/**
 * Отримання категорії за ID
 */
export const fetchCategoryByIdAsync = createAsyncThunk(
  'categories/fetchCategoryById',
  async (id: string) => {
    const token = localStorage.getItem('access_token');
    const response = await axios.get(`${API_URL}/api/categories/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  }
);

/**
 * Створення нової категорії
 */
export const createCategoryAsync = createAsyncThunk(
  'categories/createCategory',
  async (data: CreateCategoryData, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.post(`${API_URL}/api/categories`, data, {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 400 && error.response?.data?.detail?.includes('already exists')) {
        return rejectWithValue('Категорія з такою назвою вже існує');
      }
      return rejectWithValue(error.response?.data?.detail || 'Помилка при створенні категорії');
    }
  }
);

/**
 * Оновлення категорії (PUT)
 */
export const updateCategoryAsync = createAsyncThunk(
  'categories/updateCategory',
  async ({ id, data }: { id: string; data: UpdateCategoryData }, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.put(`${API_URL}/api/categories/${id}`, data, {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 400 && error.response?.data?.detail?.includes('already exists')) {
        return rejectWithValue('Категорія з такою назвою вже існує');
      }
      return rejectWithValue(error.response?.data?.detail || 'Помилка при оновленні категорії');
    }
  }
);

/**
 * Деактивація категорії
 */
export const deactivateCategoryAsync = createAsyncThunk(
  'categories/deactivateCategory',
  async (id: string, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        return rejectWithValue('Не знайдено токен автентифікації. Будь ласка, увійдіть знову.');
      }
      const response = await axios.post(
        `${API_URL}/api/categories/${id}/deactivate`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 401) {
        return rejectWithValue('Сесія застаріла. Будь ласка, увійдіть знову.');
      }
      return rejectWithValue(error.response?.data?.detail || 'Помилка при деактивації категорії');
    }
  }
);

/**
 * Активація категорії
 */
export const activateCategoryAsync = createAsyncThunk(
  'categories/activateCategory',
  async (id: string, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        return rejectWithValue('Не знайдено токен автентифікації. Будь ласка, увійдіть знову.');
      }
      const response = await axios.post(
        `${API_URL}/api/categories/${id}/activate`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 401) {
        return rejectWithValue('Сесія застаріла. Будь ласка, увійдіть знову.');
      }
      return rejectWithValue(error.response?.data?.detail || 'Помилка при активації категорії');
    }
  }
);

// Slice
const categoriesSlice = createSlice({
  name: 'categories',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearCurrentCategory: (state) => {
      state.currentCategory = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch Categories
    builder.addCase(fetchCategoriesAsync.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(fetchCategoriesAsync.fulfilled, (state, action) => {
      state.isLoading = false;
      // API повертає { categories: [...], total: N }
      state.categories = action.payload.categories || [];
      state.total = action.payload.total || 0;
    });
    builder.addCase(fetchCategoriesAsync.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.error.message || 'Помилка при завантаженні категорій';
    });

    // Fetch Category By ID
    builder.addCase(fetchCategoryByIdAsync.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(fetchCategoryByIdAsync.fulfilled, (state, action) => {
      state.isLoading = false;
      state.currentCategory = action.payload;
    });
    builder.addCase(fetchCategoryByIdAsync.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.error.message || 'Помилка при завантаженні категорії';
    });

    // Create Category
    builder.addCase(createCategoryAsync.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(createCategoryAsync.fulfilled, (state, action) => {
      state.isLoading = false;
      state.categories.unshift(action.payload);
      state.total += 1;
    });
    builder.addCase(createCategoryAsync.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string || 'Помилка при створенні категорії';
    });

    // Update Category
    builder.addCase(updateCategoryAsync.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(updateCategoryAsync.fulfilled, (state, action) => {
      state.isLoading = false;
      const index = state.categories.findIndex((cat) => cat.id === action.payload.id);
      if (index !== -1) {
        state.categories[index] = action.payload;
      }
      if (state.currentCategory?.id === action.payload.id) {
        state.currentCategory = action.payload;
      }
    });
    builder.addCase(updateCategoryAsync.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string || 'Помилка при оновленні категорії';
    });

    // Deactivate Category
    builder.addCase(deactivateCategoryAsync.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(deactivateCategoryAsync.fulfilled, (state, action) => {
      state.isLoading = false;
      const index = state.categories.findIndex((cat) => cat.id === action.payload.id);
      if (index !== -1) {
        state.categories[index] = action.payload;
      }
    });
    builder.addCase(deactivateCategoryAsync.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string || 'Помилка при деактивації категорії';
    });

    // Activate Category
    builder.addCase(activateCategoryAsync.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(activateCategoryAsync.fulfilled, (state, action) => {
      state.isLoading = false;
      const index = state.categories.findIndex((cat) => cat.id === action.payload.id);
      if (index !== -1) {
        state.categories[index] = action.payload;
      }
    });
    builder.addCase(activateCategoryAsync.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string || 'Помилка при активації категорії';
    });
  },
});

// Селектори
export const selectCategories = (state: any) => state.categories?.categories || [];
export const selectCategoriesTotal = (state: any) => state.categories?.total || 0;
export const selectCategoriesLoading = (state: any) => state.categories?.isLoading || false;
export const selectCategoriesError = (state: any) => state.categories?.error || null;
export const selectCurrentCategory = (state: any) => state.categories?.currentCategory || null;

export const { clearError, clearCurrentCategory } = categoriesSlice.actions;
export default categoriesSlice.reducer;
