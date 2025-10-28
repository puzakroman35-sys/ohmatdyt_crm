/**
 * Dashboard Page
 * Ohmatdyt CRM
 */

import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import { Row, Col, Card, Statistic, Typography, Spin } from 'antd';
import {
  FileTextOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import MainLayout from '@/components/Layout/MainLayout';
import { AuthGuard } from '@/components/Auth';
import { useAppSelector } from '@/store/hooks';
import { selectUser } from '@/store/slices/authSlice';

const { Title } = Typography;

const DashboardPage: React.FC = () => {
  const router = useRouter();
  const user = useAppSelector(selectUser);

  useEffect(() => {
    // Якщо не ADMIN - редіректимо на cases
    if (user && user.role !== 'ADMIN') {
      router.replace('/cases');
    }
  }, [user, router]);

  // Показуємо loading якщо ще немає інформації про користувача
  if (!user) {
    return (
      <AuthGuard>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          minHeight: '100vh' 
        }}>
          <Spin size="large" tip="Завантаження..." />
        </div>
      </AuthGuard>
    );
  }

  // Якщо не ADMIN, показуємо loading під час редіректу
  if (user.role !== 'ADMIN') {
    return (
      <AuthGuard>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          minHeight: '100vh' 
        }}>
          <Spin size="large" tip="Перенаправлення..." />
        </div>
      </AuthGuard>
    );
  }

  // TODO: Замінити на реальні дані з API
  const stats = {
    total: 0,
    inProgress: 0,
    completed: 0,
    needsInfo: 0,
  };

  return (
    <AuthGuard>
      <MainLayout>
        <Title level={2} style={{ marginBottom: 24 }}>
          Головна панель
        </Title>

        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Всього звернень"
                value={stats.total}
                prefix={<FileTextOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="В роботі"
                value={stats.inProgress}
                prefix={<ClockCircleOutlined />}
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Потребують інформації"
                value={stats.needsInfo}
                prefix={<ExclamationCircleOutlined />}
                valueStyle={{ color: '#ff4d4f' }}
              />
            </Card>
          </Col>

          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Завершено"
                value={stats.completed}
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
        </Row>

        <Card
          title="Останні звернення"
          style={{ marginTop: 24 }}
        >
          {/* TODO: Додати таблицю останніх звернень */}
          <p style={{ color: '#999', textAlign: 'center', padding: 40 }}>
            Поки немає звернень
          </p>
        </Card>
      </MainLayout>
    </AuthGuard>
  );
};

export default DashboardPage;
