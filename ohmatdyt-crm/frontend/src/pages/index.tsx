import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import { Spin } from 'antd';
import { useAppSelector } from '@/store/hooks';
import { selectIsAuthenticated, selectUser } from '@/store/slices/authSlice';

const HomePage: React.FC = () => {
  const router = useRouter();
  const isAuthenticated = useAppSelector(selectIsAuthenticated);
  const user = useAppSelector(selectUser);

  useEffect(() => {
    // Редіректимо на відповідну сторінку
    if (isAuthenticated && user) {
      // ADMIN на dashboard, інші на cases
      if (user.role === 'ADMIN') {
        router.push('/dashboard');
      } else {
        router.push('/cases');
      }
    } else if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, user, router]);

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
};

export default HomePage;