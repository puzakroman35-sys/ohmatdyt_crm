/**
 * Stats Summary Component
 * Ohmatdyt CRM - FE-301
 * 
 * Віджет з загальною статистикою звернень (5 карток)
 */

import React from 'react';
import { Row, Col, Card, Statistic, Spin, Alert } from 'antd';
import {
  FileTextOutlined,
  PlusCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  CloseCircleOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { DashboardSummary } from '@/types/dashboard';

interface StatsSummaryProps {
  data: DashboardSummary | null;
  loading: boolean;
  error: string | null;
}

const StatsSummary: React.FC<StatsSummaryProps> = ({ data, loading, error }) => {
  if (error) {
    return (
      <Alert
        message="Помилка завантаження статистики"
        description={error}
        type="error"
        showIcon
      />
    );
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '40px 0' }}>
        <Spin size="large" tip="Завантаження статистики..." />
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <Row gutter={[16, 16]}>
      {/* Всього звернень */}
      <Col xs={24} sm={12} lg={8} xl={24 / 5}>
        <Card>
          <Statistic
            title="Всього звернень"
            value={data.total_cases}
            prefix={<FileTextOutlined />}
            valueStyle={{ color: '#1890ff' }}
          />
        </Card>
      </Col>

      {/* Нові */}
      <Col xs={24} sm={12} lg={8} xl={24 / 5}>
        <Card>
          <Statistic
            title="Нові"
            value={data.new_cases}
            prefix={<PlusCircleOutlined />}
            valueStyle={{ color: '#52c41a' }}
          />
        </Card>
      </Col>

      {/* В роботі */}
      <Col xs={24} sm={12} lg={8} xl={24 / 5}>
        <Card>
          <Statistic
            title="В роботі"
            value={data.in_progress_cases}
            prefix={<ClockCircleOutlined />}
            valueStyle={{ color: '#faad14' }}
          />
        </Card>
      </Col>

      {/* Потребують інформації */}
      <Col xs={24} sm={12} lg={8} xl={24 / 5}>
        <Card>
          <Statistic
            title="Потребують інформації"
            value={data.needs_info_cases}
            prefix={<ExclamationCircleOutlined />}
            valueStyle={{ color: '#ff4d4f' }}
          />
        </Card>
      </Col>

      {/* Завершено */}
      <Col xs={24} sm={12} lg={8} xl={24 / 5}>
        <Card>
          <Statistic
            title="Завершено"
            value={data.done_cases}
            prefix={<CheckCircleOutlined />}
            valueStyle={{ color: '#722ed1' }}
          />
        </Card>
      </Col>
    </Row>
  );
};

export default StatsSummary;
