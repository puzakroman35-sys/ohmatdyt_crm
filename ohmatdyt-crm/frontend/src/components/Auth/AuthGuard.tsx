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
  // Завжди починаємо з isChecking = true, щоб на сервері і клієнті був однаковий вигляд
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    // Невелика затримка для завершення ініціалізації AuthProvider
    const timer = setTimeout(() => {
      // Перевіряємо авторизацію
      if (!isAuthenticated) {
        // Зберігаємо поточний URL для редіректу після логіну
        const returnUrl = router.asPath;
        router.push(`/login?returnUrl=${encodeURIComponent(returnUrl)}`);
      } else {
        setIsChecking(false);
      }
    }, 100);

    return () => clearTimeout(timer);
  }, [isAuthenticated, router]);

  // Завжди показуємо spinner поки перевіряємо авторизацію
  // Це забезпечує однаковий рендер на сервері та клієнті
  if (isChecking) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
        }}
        suppressHydrationWarning
      >
        <Spin size="large" />
      </div>
    );
  }

  return <>{children}</>;
};
