/**
 * Top Categories Chart Component
 * Ohmatdyt CRM - FE-301
 * 
 * Bar chart з топ-N категорій по кількості звернень
 */

import React from 'react';
import { Card, Spin, Alert, Empty, List, Tag, Progress } from 'antd';
import { TrophyOutlined } from '@ant-design/icons';
import { CategoriesTop, CategoryTopItem } from '@/types/dashboard';

interface TopCategoriesChartProps {
  data: CategoriesTop | null;
  loading: boolean;
  error: string | null;
}

const TopCategoriesChart: React.FC<TopCategoriesChartProps> = ({
  data,
  loading,
  error,
}) => {
  if (error) {
    return (
      <Card title={<span><TrophyOutlined /> ТОП категорій</span>}>
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
      <Card title={<span><TrophyOutlined /> ТОП категорій</span>}>
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <Spin size="large" tip="Завантаження..." />
        </div>
      </Card>
    );
  }

  if (!data || data.top_categories.length === 0) {
    return (
      <Card title={<span><TrophyOutlined /> ТОП категорій</span>}>
        <Empty description="Немає даних" />
      </Card>
    );
  }

  // Знаходимо максимальну кількість для нормалізації прогрес-барів
  const maxCount = Math.max(...data.top_categories.map((cat) => cat.total_cases));

  const getMedalEmoji = (index: number) => {
    if (index === 0) return '🥇';
    if (index === 1) return '🥈';
    if (index === 2) return '🥉';
    return `${index + 1}.`;
  };

  return (
    <Card 
      title={
        <span>
          <TrophyOutlined style={{ marginRight: 8 }} />
          ТОП-{data.limit} категорій
        </span>
      }
    >
      <List
        dataSource={data.top_categories}
        renderItem={(item: CategoryTopItem, index: number) => (
          <List.Item>
            <div style={{ width: '100%' }}>
              {/* Заголовок */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: 8,
                }}
              >
                <span style={{ fontWeight: 'bold', fontSize: '16px' }}>
                  {getMedalEmoji(index)} {item.category_name}
                </span>
                <span style={{ fontWeight: 'bold', fontSize: '14px' }}>
                  {item.total_cases} ({item.percentage_of_total.toFixed(1)}%)
                </span>
              </div>

              {/* Прогрес-бар */}
              <Progress
                percent={(item.total_cases / maxCount) * 100}
                strokeColor={
                  index === 0
                    ? '#ffd700'
                    : index === 1
                    ? '#c0c0c0'
                    : index === 2
                    ? '#cd7f32'
                    : '#1890ff'
                }
                showInfo={false}
              />

              {/* Деталі по статусах */}
              <div
                style={{
                  display: 'flex',
                  gap: 8,
                  marginTop: 8,
                  flexWrap: 'wrap',
                }}
              >
                {item.new_cases > 0 && (
                  <Tag color="green">Нові: {item.new_cases}</Tag>
                )}
                {item.in_progress_cases > 0 && (
                  <Tag color="orange">В роботі: {item.in_progress_cases}</Tag>
                )}
                {item.completed_cases > 0 && (
                  <Tag color="purple">Завершені: {item.completed_cases}</Tag>
                )}
              </div>
            </div>
          </List.Item>
        )}
      />

      <div
        style={{
          marginTop: 16,
          textAlign: 'center',
          color: '#8c8c8c',
        }}
      >
        Всього звернень у всіх категоріях: <strong>{data.total_cases_all_categories}</strong>
      </div>
    </Card>
  );
};

export default TopCategoriesChart;
