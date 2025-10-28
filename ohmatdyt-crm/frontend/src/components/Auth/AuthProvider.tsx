/**
 * Auth Provider - Відновлення стану авторизації з localStorage
 * Ohmatdyt CRM
 */

import React, { useEffect } from 'react';
import { useAppDispatch } from '@/store/hooks';
import { loginSuccess } from '@/store/slices/authSlice';

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const dispatch = useAppDispatch();

  useEffect(() => {
    // Відновлюємо стан авторизації з localStorage тільки на клієнті
    try {
      const savedState = localStorage.getItem('auth');
      if (savedState) {
        const parsed = JSON.parse(savedState);
        if (parsed.user && parsed.accessToken) {
          dispatch(
            loginSuccess({
              user: parsed.user,
              accessToken: parsed.accessToken,
              refreshToken: parsed.refreshToken || '',
            })
          );
        }
      }
    } catch (error) {
      console.error('Failed to restore auth state:', error);
    }
  }, [dispatch]);

  return <>{children}</>;
};

export default AuthProvider;
