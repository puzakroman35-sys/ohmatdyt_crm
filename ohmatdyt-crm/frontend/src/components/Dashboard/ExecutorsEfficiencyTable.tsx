/**
 * Executors Efficiency Table Component
 * Ohmatdyt CRM - FE-301
 * 
 * Таблиця ефективності виконавців з сортуванням
 */

import React from 'react';
import { Card, Table, Tag, Spin, Alert, Empty, Tooltip } from 'antd';
import { UserOutlined, TrophyOutlined } from '@ant-design/icons';
import { ExecutorEfficiency, ExecutorEfficiencyItem } from '@/types/dashboard';
import { ColumnsType } from 'antd/es/table';

interface ExecutorsEfficiencyTableProps {
  data: ExecutorEfficiency | null;
  loading: boolean;
  error: string | null;
}

const ExecutorsEfficiencyTable: React.FC<ExecutorsEfficiencyTableProps> = ({
  data,
  loading,
  error,
}) => {
  const columns: ColumnsType<ExecutorEfficiencyItem> = [
    {
      title: 'Виконавець',
      dataIndex: 'full_name',
      key: 'full_name',
      fixed: 'left',
      width: 200,
      render: (name: string, record: ExecutorEfficiencyItem) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>
            <UserOutlined style={{ marginRight: 8 }} />
            {name}
          </div>
          <div style={{ fontSize: '12px', color: '#8c8c8c' }}>{record.email}</div>
        </div>
      ),
    },
    {
      title: 'Категорії',
      dataIndex: 'categories',
      key: 'categories',
      width: 250,
      render: (categories: string[]) => (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
          {categories.length === 0 ? (
            <span style={{ color: '#8c8c8c' }}>Немає категорій</span>
          ) : (
            categories.map((cat, idx) => (
              <Tag key={idx} color="blue" style={{ margin: 0 }}>
                {cat}
              </Tag>
            ))
          )}
        </div>
      ),
    },
    {
      title: 'В роботі зараз',
      dataIndex: 'current_in_progress',
      key: 'current_in_progress',
      width: 140,
      align: 'center',
      sorter: (a, b) => a.current_in_progress - b.current_in_progress,
      render: (count: number) => (
        <Tag color={count > 10 ? 'red' : count > 5 ? 'orange' : 'green'}>
          {count}
        </Tag>
      ),
    },
    {
      title: 'Завершено в періоді',
      dataIndex: 'completed_in_period',
      key: 'completed_in_period',
      width: 160,
      align: 'center',
      sorter: (a, b) => a.completed_in_period - b.completed_in_period,
      render: (count: number) => (
        <Tag color="purple">
          {count}
        </Tag>
      ),
    },
    {
      title: 'Середній час (дні)',
      dataIndex: 'avg_completion_days',
      key: 'avg_completion_days',
      width: 150,
      align: 'center',
      sorter: (a, b) => {
        const aVal = a.avg_completion_days ?? Infinity;
        const bVal = b.avg_completion_days ?? Infinity;
        return aVal - bVal;
      },
      render: (days: number | null) => {
        if (days === null) {
          return <span style={{ color: '#8c8c8c' }}>—</span>;
        }
        return (
          <Tooltip title="Середній час завершення звернення">
            <Tag color={days < 3 ? 'green' : days < 7 ? 'orange' : 'red'}>
              {days.toFixed(1)} дн.
            </Tag>
          </Tooltip>
        );
      },
    },
    {
      title: 'Прострочені',
      dataIndex: 'overdue_count',
      key: 'overdue_count',
      width: 130,
      align: 'center',
      sorter: (a, b) => a.overdue_count - b.overdue_count,
      render: (count: number) => (
        <Tag color={count > 0 ? 'red' : 'green'} icon={count > 0 ? <TrophyOutlined /> : undefined}>
          {count}
        </Tag>
      ),
    },
  ];

  if (error) {
    return (
      <Card title="Ефективність виконавців">
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
      <Card title="Ефективність виконавців">
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <Spin size="large" tip="Завантаження..." />
        </div>
      </Card>
    );
  }

  if (!data || data.executors.length === 0) {
    return (
      <Card title="Ефективність виконавців">
        <Empty description="Немає даних про виконавців" />
      </Card>
    );
  }

  return (
    <Card title="Ефективність виконавців">
      <Table
        dataSource={data.executors}
        columns={columns}
        rowKey="user_id"
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showTotal: (total) => `Всього виконавців: ${total}`,
        }}
        scroll={{ x: 1200 }}
      />
    </Card>
  );
};

export default ExecutorsEfficiencyTable;
