/**
 * Auth Slice - Управління станом автентифікації
 * Ohmatdyt CRM
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit';

// Типи
export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: 'OPERATOR' | 'EXECUTOR' | 'ADMIN';
  is_active: boolean;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// Завантаження стану з localStorage
const loadStateFromStorage = (): Partial<AuthState> => {
  if (typeof window === 'undefined') {
    return {
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    };
  }

  try {
    const savedState = localStorage.getItem('auth');
    if (savedState) {
      const parsed = JSON.parse(savedState);
      // Також відновлюємо окремий токен для сумісності
      if (parsed.accessToken) {
        localStorage.setItem('access_token', parsed.accessToken);
      }
      return {
        user: parsed.user || null,
        accessToken: parsed.accessToken || null,
        refreshToken: parsed.refreshToken || null,
        isAuthenticated: !!parsed.accessToken,
      };
    }
  } catch (error) {
    console.error('Failed to load auth state from localStorage:', error);
  }

  return {
    user: null,
    accessToken: null,
    refreshToken: null,
    isAuthenticated: false,
  };
};

// Збереження стану в localStorage
const saveStateToStorage = (state: AuthState) => {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    const stateToSave = {
      user: state.user,
      accessToken: state.accessToken,
      refreshToken: state.refreshToken,
    };
    localStorage.setItem('auth', JSON.stringify(stateToSave));
    
    // Також зберігаємо токен окремо для сумісності з іншими частинами коду
    if (state.accessToken) {
      localStorage.setItem('access_token', state.accessToken);
    }
  } catch (error) {
    console.error('Failed to save auth state to localStorage:', error);
  }
};

// Очищення localStorage
const clearStorage = () => {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    localStorage.removeItem('auth');
    localStorage.removeItem('access_token'); // Також очищаємо окремий токен
  } catch (error) {
    console.error('Failed to clear auth state from localStorage:', error);
  }
};

// Початковий стан
const loadedState = loadStateFromStorage();
const initialState: AuthState = {
  user: loadedState.user || null,
  accessToken: loadedState.accessToken || null,
  refreshToken: loadedState.refreshToken || null,
  isAuthenticated: loadedState.isAuthenticated || false,
  isLoading: false,
  error: null,
};

// Slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    // Початок логіну
    loginStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    
    // Успішний логін
    loginSuccess: (
      state,
      action: PayloadAction<{
        user: User;
        accessToken: string;
        refreshToken: string;
      }>
    ) => {
      state.isLoading = false;
      state.isAuthenticated = true;
      state.user = action.payload.user;
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      state.error = null;
      
      // Зберігаємо в localStorage
      saveStateToStorage(state);
    },
    
    // Помилка логіну
    loginFailure: (state, action: PayloadAction<string>) => {
      state.isLoading = false;
      state.isAuthenticated = false;
      state.error = action.payload;
    },
    
    // Logout
    logout: (state) => {
      state.user = null;
      state.accessToken = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      state.error = null;
      
      // Очищаємо localStorage
      clearStorage();
    },
    
    // Оновлення токену
    updateTokens: (
      state,
      action: PayloadAction<{
        accessToken: string;
        refreshToken: string;
      }>
    ) => {
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      
      // Зберігаємо в localStorage
      saveStateToStorage(state);
    },
    
    // Очистити помилку
    clearError: (state) => {
      state.error = null;
    },
  },
});

// Експорт actions
export const {
  loginStart,
  loginSuccess,
  loginFailure,
  logout,
  updateTokens,
  clearError,
} = authSlice.actions;

// Селектори
export const selectAuth = (state: any) => state.auth || {};
export const selectUser = (state: any) => state.auth?.user || null;
export const selectIsAuthenticated = (state: any) =>
  state.auth?.isAuthenticated || false;
export const selectUserRole = (state: any) =>
  state.auth?.user?.role || null;

// Експорт reducer
export default authSlice.reducer;
