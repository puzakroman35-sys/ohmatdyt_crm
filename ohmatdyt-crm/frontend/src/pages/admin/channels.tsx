/**
 * Channels Page
 * Ohmatdyt CRM - Управління каналами зв'язку (тільки для ADMIN)
 */

import React, { useEffect, useState } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Input,
  Row,
  Col,
  Typography,
  Alert,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import { useDispatch, useSelector } from 'react-redux';
import type { ColumnsType, TablePaginationConfig } from 'antd/es/table';
import MainLayout from '@/components/Layout/MainLayout';
import { AuthGuard } from '@/components/Auth';
import { AppDispatch } from '@/store';
import {
  fetchChannelsAsync,
  selectChannels,
  selectChannelsTotal,
  selectChannelsLoading,
  Channel,
} from '@/store/slices/channelsSlice';
import { selectUser } from '@/store/slices/authSlice';
import {
  CreateChannelForm,
  EditChannelForm,
  DeactivateChannelButton,
  ActivateChannelButton,
} from '@/components/Channels';
import dayjs from 'dayjs';

const { Title } = Typography;

const ChannelsPage: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const channels = useSelector(selectChannels);
  const total = useSelector(selectChannelsTotal);
  const isLoading = useSelector(selectChannelsLoading);
  const user = useSelector(selectUser);

  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [selectedChannel, setSelectedChannel] = useState<Channel | null>(null);

  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
  });
  const [searchText, setSearchText] = useState('');
  const [includeInactive, setIncludeInactive] = useState(true);

  // Завантаження даних
  const loadData = () => {
    dispatch(
      fetchChannelsAsync({
        skip: (pagination.current - 1) * pagination.pageSize,
        limit: pagination.pageSize,
        search: searchText || undefined,
        include_inactive: includeInactive,
      })
    );
  };

  useEffect(() => {
    loadData();
  }, [pagination.current, pagination.pageSize, searchText, includeInactive]);

  // Обробники
  const handleTableChange = (newPagination: TablePaginationConfig) => {
    setPagination({
      current: newPagination.current || 1,
      pageSize: newPagination.pageSize || 10,
    });
  };

  const handleSearch = (value: string) => {
    setSearchText(value);
    setPagination({ ...pagination, current: 1 });
  };

  const handleEdit = (channel: Channel) => {
    setSelectedChannel(channel);
    setEditModalVisible(true);
  };

  const handleActionSuccess = () => {
    loadData();
  };

  // RBAC перевірка
  const userRole = user?.role;
  const hasAccess = userRole === 'ADMIN';

  if (!hasAccess) {
    return (
      <AuthGuard>
        <MainLayout>
          <Alert
            message="Доступ заборонено"
            description="Тільки адміністратори мають доступ до управління каналами зв'язку."
            type="error"
            showIcon
          />
        </MainLayout>
      </AuthGuard>
    );
  }

  // Колонки таблиці
  const columns: ColumnsType<Channel> = [
    {
      title: 'Назва каналу',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: Channel) => (
        <Space>
          <span>{name}</span>
          {!record.is_active && (
            <Tag color="red">Деактивовано</Tag>
          )}
        </Space>
      ),
    },
    {
      title: 'Статус',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 120,
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? 'Активний' : 'Неактивний'}
        </Tag>
      ),
    },
    {
      title: 'Дата створення',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => dayjs(date).format('DD.MM.YYYY HH:mm'),
    },
    {
      title: 'Дії',
      key: 'actions',
      fixed: 'right',
      width: 300,
      render: (_, record: Channel) => (
        <Space size="small" wrap>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Редагувати
          </Button>
          <DeactivateChannelButton
            channel={record}
            onSuccess={handleActionSuccess}
          />
          <ActivateChannelButton
            channel={record}
            onSuccess={handleActionSuccess}
          />
        </Space>
      ),
    },
  ];

  return (
    <AuthGuard>
      <MainLayout>
        <div style={{ padding: '24px' }}>
          <Card>
            <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
              <Col>
                <Title level={2} style={{ margin: 0 }}>
                  Управління каналами зв'язку
                </Title>
              </Col>
              <Col>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  size="large"
                  onClick={() => setCreateModalVisible(true)}
                >
                  Створити канал
            </Button>
          </Col>
        </Row>

        {/* Фільтри */}
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={24} sm={12} md={8}>
            <Input
              placeholder="Пошук за назвою..."
              prefix={<SearchOutlined />}
              allowClear
              onChange={(e) => handleSearch(e.target.value)}
              size="large"
            />
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Button
              size="large"
              type={includeInactive ? 'primary' : 'default'}
              onClick={() => setIncludeInactive(!includeInactive)}
            >
              {includeInactive ? 'Показано всі' : 'Тільки активні'}
            </Button>
          </Col>
        </Row>

        {/* Таблиця */}
        <Table
          columns={columns}
          dataSource={channels || []}
          rowKey="id"
          loading={isLoading}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: total,
            showSizeChanger: true,
            showTotal: (total) => `Всього: ${total}`,
            pageSizeOptions: ['10', '20', '50', '100'],
          }}
          onChange={handleTableChange}
          scroll={{ x: 800 }}
        />
      </Card>

      {/* Модальні вікна */}
      <CreateChannelForm
        visible={createModalVisible}
        onClose={() => setCreateModalVisible(false)}
        onSuccess={handleActionSuccess}
      />

      <EditChannelForm
        visible={editModalVisible}
        channel={selectedChannel}
        onClose={() => {
          setEditModalVisible(false);
          setSelectedChannel(null);
        }}
        onSuccess={handleActionSuccess}
      />
        </div>
      </MainLayout>
    </AuthGuard>
  );
};

export default ChannelsPage;
