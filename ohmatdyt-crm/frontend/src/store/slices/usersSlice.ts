/**
 * Users Slice - Управління станом користувачів
 * Ohmatdyt CRM - FE-008
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import api from '@/lib/api';

// Типи
export type UserRole = 'OPERATOR' | 'EXECUTOR' | 'ADMIN';

export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  executor_category_ids?: string[];
  created_at: string;
  updated_at: string;
}

export interface CreateUserData {
  username: string;
  email: string;
  full_name: string;
  password: string;
  role: UserRole;
  is_active?: boolean;
  executor_category_ids?: string[];
}

export interface UpdateUserData {
  username?: string;
  email?: string;
  full_name?: string;
  password?: string;
  role?: UserRole;
  is_active?: boolean;
  executor_category_ids?: string[];
}

export interface UsersFilters {
  role?: UserRole;
  is_active?: boolean;
  search?: string;
}

export interface UsersPagination {
  skip: number;
  limit: number;
}

export interface UsersSort {
  field: string;
  order: 'asc' | 'desc';
}

export interface UsersState {
  users: User[];
  total: number;
  isLoading: boolean;
  error: string | null;
  currentUser: User | null; // Для детальної інформації/редагування
}

// Початковий стан
const initialState: UsersState = {
  users: [],
  total: 0,
  isLoading: false,
  error: null,
  currentUser: null,
};

// Async Thunks

// Отримати список користувачів
export const fetchUsersAsync = createAsyncThunk(
  'users/fetchUsers',
  async (
    params: {
      filters?: UsersFilters;
      pagination?: UsersPagination;
      sort?: UsersSort;
    },
    { rejectWithValue }
  ) => {
    try {
      const { filters = {}, pagination = { skip: 0, limit: 20 }, sort = { field: 'created_at', order: 'desc' } } = params;

      // Побудова query parameters
      const queryParams: Record<string, any> = {
        skip: pagination.skip,
        limit: pagination.limit,
      };

      if (filters.role) queryParams.role = filters.role;
      if (filters.is_active !== undefined) queryParams.is_active = filters.is_active;
      if (filters.search) queryParams.search = filters.search;

      // Сортування
      queryParams.order_by = sort.field;
      queryParams.order = sort.order;

      const response = await api.get('/api/users', { params: queryParams });
      
      return {
        users: response.data.users || response.data,
        total: response.data.total || (response.data.users ? response.data.users.length : response.data.length),
      };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Помилка завантаження користувачів');
    }
  }
);

// Отримати користувача за ID
export const fetchUserByIdAsync = createAsyncThunk(
  'users/fetchUserById',
  async (userId: string, { rejectWithValue }) => {
    try {
      const response = await api.get(`/api/users/${userId}`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Помилка завантаження користувача');
    }
  }
);

// Створити користувача
export const createUserAsync = createAsyncThunk(
  'users/createUser',
  async (userData: CreateUserData, { rejectWithValue }) => {
    try {
      const response = await api.post('/api/users', userData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Помилка створення користувача');
    }
  }
);

// Оновити користувача (повністю)
export const updateUserAsync = createAsyncThunk(
  'users/updateUser',
  async (
    params: { userId: string; userData: UpdateUserData },
    { rejectWithValue }
  ) => {
    try {
      const response = await api.put(`/api/users/${params.userId}`, params.userData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Помилка оновлення користувача');
    }
  }
);

// Оновити користувача (частково)
export const patchUserAsync = createAsyncThunk(
  'users/patchUser',
  async (
    params: { userId: string; userData: Partial<UpdateUserData> },
    { rejectWithValue }
  ) => {
    try {
      const response = await api.patch(`/api/users/${params.userId}`, params.userData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Помилка оновлення користувача');
    }
  }
);

// Деактивувати користувача
export const deactivateUserAsync = createAsyncThunk(
  'users/deactivateUser',
  async (
    params: { userId: string; force?: boolean },
    { rejectWithValue }
  ) => {
    try {
      const response = await api.post(
        `/api/users/${params.userId}/deactivate`,
        null,
        { params: { force: params.force || false } }
      );
      return response.data;
    } catch (error: any) {
      // Спеціальна обробка 409 Conflict (користувач має активні справи)
      if (error.response?.status === 409) {
        return rejectWithValue({
          message: error.response?.data?.detail || 'Користувач має активні справи',
          hasActiveCases: true,
          activeCasesCount: error.response?.data?.active_cases_count,
        });
      }
      return rejectWithValue(error.response?.data?.detail || 'Помилка деактивації користувача');
    }
  }
);

// Активувати користувача
export const activateUserAsync = createAsyncThunk(
  'users/activateUser',
  async (userId: string, { rejectWithValue }) => {
    try {
      const response = await api.post(`/api/users/${userId}/activate`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Помилка активації користувача');
    }
  }
);

// Скинути пароль
export const resetPasswordAsync = createAsyncThunk(
  'users/resetPassword',
  async (userId: string, { rejectWithValue }) => {
    try {
      const response = await api.post(`/api/users/${userId}/reset-password`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Помилка скидання пароля');
    }
  }
);

// Отримати активні справи користувача
export const fetchUserActiveCasesAsync = createAsyncThunk(
  'users/fetchUserActiveCases',
  async (userId: string, { rejectWithValue }) => {
    try {
      const response = await api.get(`/api/users/${userId}/active-cases`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Помилка завантаження активних справ');
    }
  }
);

// Slice
const usersSlice = createSlice({
  name: 'users',
  initialState,
  reducers: {
    // Очистити помилку
    clearError: (state) => {
      state.error = null;
    },
    // Очистити поточного користувача
    clearCurrentUser: (state) => {
      state.currentUser = null;
    },
    // Встановити поточного користувача
    setCurrentUser: (state, action: PayloadAction<User>) => {
      state.currentUser = action.payload;
    },
  },
  extraReducers: (builder) => {
    // Fetch Users
    builder
      .addCase(fetchUsersAsync.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchUsersAsync.fulfilled, (state, action) => {
        state.isLoading = false;
        state.users = action.payload.users;
        state.total = action.payload.total;
      })
      .addCase(fetchUsersAsync.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Fetch User By ID
    builder
      .addCase(fetchUserByIdAsync.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchUserByIdAsync.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentUser = action.payload;
      })
      .addCase(fetchUserByIdAsync.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Create User
    builder
      .addCase(createUserAsync.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createUserAsync.fulfilled, (state, action) => {
        state.isLoading = false;
        // Додаємо нового користувача на початок списку
        state.users = [action.payload, ...state.users];
        state.total += 1;
      })
      .addCase(createUserAsync.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Update User
    builder
      .addCase(updateUserAsync.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateUserAsync.fulfilled, (state, action) => {
        state.isLoading = false;
        // Оновлюємо користувача в списку
        const index = state.users.findIndex((u) => u.id === action.payload.id);
        if (index !== -1) {
          state.users[index] = action.payload;
        }
        // Оновлюємо currentUser якщо це він
        if (state.currentUser?.id === action.payload.id) {
          state.currentUser = action.payload;
        }
      })
      .addCase(updateUserAsync.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Patch User
    builder
      .addCase(patchUserAsync.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(patchUserAsync.fulfilled, (state, action) => {
        state.isLoading = false;
        // Оновлюємо користувача в списку
        const index = state.users.findIndex((u) => u.id === action.payload.id);
        if (index !== -1) {
          state.users[index] = action.payload;
        }
        // Оновлюємо currentUser якщо це він
        if (state.currentUser?.id === action.payload.id) {
          state.currentUser = action.payload;
        }
      })
      .addCase(patchUserAsync.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Deactivate User
    builder
      .addCase(deactivateUserAsync.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(deactivateUserAsync.fulfilled, (state, action) => {
        state.isLoading = false;
        // Оновлюємо користувача в списку
        const index = state.users.findIndex((u) => u.id === action.payload.id);
        if (index !== -1) {
          state.users[index] = action.payload;
        }
      })
      .addCase(deactivateUserAsync.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Activate User
    builder
      .addCase(activateUserAsync.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(activateUserAsync.fulfilled, (state, action) => {
        state.isLoading = false;
        // Оновлюємо користувача в списку
        const index = state.users.findIndex((u) => u.id === action.payload.id);
        if (index !== -1) {
          state.users[index] = action.payload;
        }
      })
      .addCase(activateUserAsync.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Reset Password
    builder
      .addCase(resetPasswordAsync.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(resetPasswordAsync.fulfilled, (state) => {
        state.isLoading = false;
      })
      .addCase(resetPasswordAsync.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Fetch Active Cases
    builder
      .addCase(fetchUserActiveCasesAsync.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchUserActiveCasesAsync.fulfilled, (state) => {
        state.isLoading = false;
      })
      .addCase(fetchUserActiveCasesAsync.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

// Експорт actions
export const { clearError, clearCurrentUser, setCurrentUser } = usersSlice.actions;

// Селектори
export const selectUsers = (state: { users: UsersState }) => state.users.users;
export const selectUsersTotal = (state: { users: UsersState }) => state.users.total;
export const selectUsersLoading = (state: { users: UsersState }) => state.users.isLoading;
export const selectUsersError = (state: { users: UsersState }) => state.users.error;
export const selectCurrentUser = (state: { users: UsersState }) => state.users.currentUser;

// Експорт reducer
export default usersSlice.reducer;
