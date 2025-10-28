/**
 * RoleGuard Component
 * Перевірка доступу на основі ролі користувача
 * Ohmatdyt CRM
 */

import React from 'react';
import { useRouter } from 'next/router';
import { Result, Button } from 'antd';
import { useAppSelector } from '@/store/hooks';
import { selectUser } from '@/store/slices/authSlice';

interface RoleGuardProps {
  children: React.ReactNode;
  allowedRoles: Array<'OPERATOR' | 'EXECUTOR' | 'ADMIN'>;
  fallbackPath?: string;
}

/**
 * Компонент для обмеження доступу на основі ролі користувача
 * Показує сторінку "Доступ заборонено" якщо роль не дозволена
 */
export const RoleGuard: React.FC<RoleGuardProps> = ({
  children,
  allowedRoles,
  fallbackPath = '/dashboard',
}) => {
  const router = useRouter();
  const user = useAppSelector(selectUser);

  // Перевіряємо чи роль користувача дозволена
  const hasAccess = user && allowedRoles.includes(user.role);

  if (!hasAccess) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
        }}
      >
        <Result
          status="403"
          title="403"
          subTitle="Вибачте, у вас немає доступу до цієї сторінки."
          extra={
            <Button type="primary" onClick={() => router.push(fallbackPath)}>
              Повернутися на головну
            </Button>
          }
        />
      </div>
    );
  }

  return <>{children}</>;
};
