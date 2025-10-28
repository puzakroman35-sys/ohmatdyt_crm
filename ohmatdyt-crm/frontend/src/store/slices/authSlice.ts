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

// Початковий стан
const initialState: AuthState = {
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
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
export const selectAuth = (state: { auth: AuthState }) => state.auth;
export const selectUser = (state: { auth: AuthState }) => state.auth.user;
export const selectIsAuthenticated = (state: { auth: AuthState }) =>
  state.auth.isAuthenticated;
export const selectUserRole = (state: { auth: AuthState }) =>
  state.auth.user?.role;

// Експорт reducer
export default authSlice.reducer;
