/**
 * Redux Store Configuration
 * Ohmatdyt CRM - Центральне сховище стану додатку
 */

import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import casesReducer from './slices/casesSlice';
import usersReducer from './slices/usersSlice';
import categoriesReducer from './slices/categoriesSlice';
import channelsReducer from './slices/channelsSlice';
import dashboardReducer from './slices/dashboardSlice'; // FE-301

export const store = configureStore({
  reducer: {
    auth: authReducer,
    cases: casesReducer,
    users: usersReducer,
    categories: categoriesReducer,
    channels: channelsReducer,
    dashboard: dashboardReducer, // FE-301
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ігноруємо перевірку серіалізації для певних actions якщо потрібно
        ignoredActions: [],
      },
    }),
});

// Типи для TypeScript
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
