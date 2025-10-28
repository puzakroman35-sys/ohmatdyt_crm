/**
 * Dashboard Page
 * Ohmatdyt CRM
 */

import React from 'react';
import { Row, Col, Card, Statistic, Typography } from 'antd';
import {
  FileTextOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import MainLayout from '@/components/Layout/MainLayout';
import { AuthGuard } from '@/components/Auth';

const { Title } = Typography;

const DashboardPage: React.FC = () => {
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
