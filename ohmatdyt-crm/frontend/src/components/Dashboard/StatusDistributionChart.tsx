/**
 * Status Distribution Chart Component
 * Ohmatdyt CRM - FE-301
 * 
 * Кругова діаграма розподілу звернень по статусах
 */

import React from 'react';
import { Card, Spin, Alert, Empty, List, Tag, Progress } from 'antd';
import { StatusDistribution } from '@/types/dashboard';
import { CaseStatus } from '@/store/slices/casesSlice';

interface StatusDistributionChartProps {
  data: StatusDistribution | null;
  loading: boolean;
  error: string | null;
}

const STATUS_LABELS: Record<CaseStatus, string> = {
  [CaseStatus.NEW]: 'Нові',
  [CaseStatus.IN_PROGRESS]: 'В роботі',
  [CaseStatus.NEEDS_INFO]: 'Потребують інформації',
  [CaseStatus.REJECTED]: 'Відхилені',
  [CaseStatus.DONE]: 'Завершені',
};

const STATUS_COLORS: Record<CaseStatus, string> = {
  [CaseStatus.NEW]: '#52c41a',
  [CaseStatus.IN_PROGRESS]: '#faad14',
  [CaseStatus.NEEDS_INFO]: '#ff4d4f',
  [CaseStatus.REJECTED]: '#8c8c8c',
  [CaseStatus.DONE]: '#722ed1',
};

const StatusDistributionChart: React.FC<StatusDistributionChartProps> = ({
  data,
  loading,
  error,
}) => {
  if (error) {
    return (
      <Card title="Розподіл по статусах">
        <Alert
          message="Помилка завантаження"
          description={error}
          type="error"
          showIcon
        />
      </Card>
    );
  }

  if (loading) {
    return (
      <Card title="Розподіл по статусах">
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <Spin size="large" tip="Завантаження..." />
        </div>
      </Card>
    );
  }

  if (!data || data.total_cases === 0) {
    return (
      <Card title="Розподіл по статусах">
        <Empty description="Немає даних" />
      </Card>
    );
  }

  return (
    <Card title="Розподіл по статусах">
      <List
        dataSource={data.distribution}
        renderItem={(item) => (
          <List.Item>
            <div style={{ width: '100%' }}>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  marginBottom: 8,
                }}
              >
                <span>
                  <Tag color={STATUS_COLORS[item.status]}>
                    {STATUS_LABELS[item.status]}
                  </Tag>
                </span>
                <span style={{ fontWeight: 'bold' }}>
                  {item.count} ({item.percentage.toFixed(1)}%)
                </span>
              </div>
              <Progress
                percent={item.percentage}
                strokeColor={STATUS_COLORS[item.status]}
                showInfo={false}
              />
            </div>
          </List.Item>
        )}
      />
      
      <div style={{ marginTop: 16, textAlign: 'center', color: '#8c8c8c' }}>
        Всього звернень: <strong>{data.total_cases}</strong>
      </div>
    </Card>
  );
};

export default StatusDistributionChart;
