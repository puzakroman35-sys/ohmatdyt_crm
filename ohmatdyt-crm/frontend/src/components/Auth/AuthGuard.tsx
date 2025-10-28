/**
 * AuthGuard Component
 * Захист маршрутів від неавторизованих користувачів
 * Ohmatdyt CRM
 */

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { Spin } from 'antd';
import { useAppSelector } from '@/store/hooks';
import { selectIsAuthenticated } from '@/store/slices/authSlice';

interface AuthGuardProps {
  children: React.ReactNode;
}

/**
 * Компонент для захисту сторінок від неавторизованих користувачів
 * Автоматично редіректить на /login якщо користувач не авторизований
 */
export const AuthGuard: React.FC<AuthGuardProps> = ({ children }) => {
  const router = useRouter();
  const isAuthenticated = useAppSelector(selectIsAuthenticated);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    // Перевіряємо авторизацію при монтуванні компонента
    if (!isAuthenticated) {
      // Зберігаємо поточний URL для редіректу після логіну
      const returnUrl = router.asPath;
      router.push(`/login?returnUrl=${encodeURIComponent(returnUrl)}`);
    } else {
      setIsChecking(false);
    }
  }, [isAuthenticated, router]);

  // Показуємо spinner під час перевірки
  if (isChecking || !isAuthenticated) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
        }}
      >
        <Spin size="large" tip="Завантаження..." />
      </div>
    );
  }

  return <>{children}</>;
};
