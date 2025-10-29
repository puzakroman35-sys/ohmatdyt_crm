/**
 * Overdue Cases List Component
 * Ohmatdyt CRM - FE-301
 * 
 * Таблиця прострочених звернень з можливістю переходу до деталей
 */

import React from 'react';
import { useRouter } from 'next/router';
import { Card, Table, Tag, Button, Spin, Alert, Empty } from 'antd';
import { EyeOutlined, WarningOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { OverdueCases, OverdueCaseItem } from '@/types/dashboard';

interface OverdueCasesListProps {
  data: OverdueCases | null;
  loading: boolean;
  error: string | null;
}

const OverdueCasesList: React.FC<OverdueCasesListProps> = ({
  data,
  loading,
  error,
}) => {
  const router = useRouter();

  const columns = [
    {
      title: 'ID',
      dataIndex: 'public_id',
      key: 'public_id',
      width: 100,
      render: (public_id: number) => (
        <Tag color="blue">#{public_id.toString().padStart(6, '0')}</Tag>
      ),
    },
    {
      title: 'Категорія',
      dataIndex: 'category_name',
      key: 'category_name',
      ellipsis: true,
    },
    {
      title: 'Заявник',
      dataIndex: 'applicant_name',
      key: 'applicant_name',
      ellipsis: true,
    },
    {
      title: 'Створено',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 120,
      render: (created_at: string) => dayjs(created_at).format('DD.MM.YYYY'),
    },
    {
      title: 'Прострочено (днів)',
      dataIndex: 'days_overdue',
      key: 'days_overdue',
      width: 160,
      render: (days: number) => (
        <Tag color="red" icon={<WarningOutlined />}>
          {days} дн.
        </Tag>
      ),
    },
    {
      title: 'Відповідальний',
      dataIndex: 'responsible_name',
      key: 'responsible_name',
      ellipsis: true,
      render: (name: string | null) => name || <span style={{ color: '#8c8c8c' }}>Не призначено</span>,
    },
    {
      title: 'Дії',
      key: 'actions',
      width: 100,
      render: (_: any, record: OverdueCaseItem) => (
        <Button
          type="link"
          icon={<EyeOutlined />}
          onClick={() => router.push(`/cases/${record.id}`)}
        >
          Деталі
        </Button>
      ),
    },
  ];

  if (error) {
    return (
      <Card 
        title={
          <span>
            <WarningOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />
            Прострочені звернення
          </span>
        }
      >
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
      <Card 
        title={
          <span>
            <WarningOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />
            Прострочені звернення
          </span>
        }
      >
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <Spin size="large" tip="Завантаження..." />
        </div>
      </Card>
    );
  }

  return (
    <Card 
      title={
        <span>
          <WarningOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />
          Прострочені звернення
          {data && data.total_overdue > 0 && (
            <Tag color="red" style={{ marginLeft: 8 }}>
              {data.total_overdue}
            </Tag>
          )}
        </span>
      }
    >
      {!data || data.total_overdue === 0 ? (
        <Empty description="Немає прострочених звернень" />
      ) : (
        <Table
          dataSource={data.cases}
          columns={columns}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: false,
            showTotal: (total) => `Всього: ${total}`,
          }}
          scroll={{ x: 800 }}
        />
      )}
    </Card>
  );
};

export default OverdueCasesList;
