/**
 * Users Management Page
 * Ohmatdyt CRM - FE-008
 * Адмін розділ для управління користувачами
 */

import React, { useEffect, useState } from 'react';
import {
  Table,
  Card,
  Typography,
  Tag,
  Space,
  Button,
  Select,
  Input,
  Row,
  Col,
  message,
  Tooltip,
} from 'antd';
import {
  UserAddOutlined,
  EditOutlined,
  SearchOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';
import MainLayout from '@/components/Layout/MainLayout';
import { AuthGuard } from '@/components/Auth';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import {
  fetchUsersAsync,
  selectUsers,
  selectUsersLoading,
  selectUsersError,
  selectUsersTotal,
  User,
  UserRole,
  clearError,
  setCurrentUser,
} from '@/store/slices/usersSlice';
import { selectUser, selectUserRole } from '@/store/slices/authSlice';
import {
  CreateUserForm,
  EditUserForm,
  DeactivateUserButton,
  ActivateUserButton,
  ResetPasswordButton,
} from '@/components/Users';

const { Title } = Typography;
const { Option } = Select;

// Лейбли для ролей
const roleLabels: Record<UserRole, string> = {
  OPERATOR: 'Оператор',
  EXECUTOR: 'Виконавець',
  ADMIN: 'Адміністратор',
};

// Кольори для ролей
const roleColors: Record<UserRole, string> = {
  OPERATOR: 'blue',
  EXECUTOR: 'green',
  ADMIN: 'red',
};

const UsersPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const currentUser = useAppSelector(selectUser);
  const userRole = useAppSelector(selectUserRole);
  const users = useAppSelector(selectUsers);
  const isLoading = useAppSelector(selectUsersLoading);
  const error = useAppSelector(selectUsersError);
  const total = useAppSelector(selectUsersTotal);

  // Перевірка доступу - тільки для ADMIN
  const hasAccess = userRole === 'ADMIN';

  // Стан модальних вікон
  const [isCreateModalVisible, setIsCreateModalVisible] = useState(false);
  const [isEditModalVisible, setIsEditModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);

  // Стан фільтрів
  const [filters, setFilters] = useState({
    role: undefined as UserRole | undefined,
    is_active: undefined as boolean | undefined,
    search: '',
  });

  // Стан пагінації
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total: number, range: [number, number]) =>
      `${range[0]}-${range[1]} з ${total} користувачів`,
  });

  // Стан сортування
  const [sorter, setSorter] = useState({
    field: 'created_at',
    order: 'descend' as 'ascend' | 'descend',
  });

  // Завантаження даних
  const loadUsers = () => {
    if (!hasAccess) return;

    const apiFilters: Record<string, any> = {};
    if (filters.role) apiFilters.role = filters.role;
    if (filters.is_active !== undefined) apiFilters.is_active = filters.is_active;
    if (filters.search) apiFilters.search = filters.search;

    const sort = {
      field: sorter.field,
      order: sorter.order === 'descend' ? 'desc' : 'asc' as 'asc' | 'desc',
    };

    dispatch(
      fetchUsersAsync({
        filters: apiFilters,
        pagination: {
          skip: (pagination.current - 1) * pagination.pageSize,
          limit: pagination.pageSize,
        },
        sort,
      })
    );
  };

  // Завантаження при монтажі та зміні фільтрів
  useEffect(() => {
    if (hasAccess) {
      loadUsers();
    }
  }, [hasAccess, pagination.current, pagination.pageSize, sorter, filters]);

  // Обробка помилок
  useEffect(() => {
    if (error) {
      message.error(error);
      dispatch(clearError());
    }
  }, [error, dispatch]);

  // Обробка зміни пагінації та сортування
  const handleTableChange = (pagination: any, filters: any, sorter: any) => {
    setPagination((prev) => ({
      ...prev,
      current: pagination.current,
      pageSize: pagination.pageSize,
    }));

    if (sorter.field && sorter.order) {
      setSorter({
        field: sorter.field,
        order: sorter.order,
      });
    }
  };

  // Відкрити модальне вікно редагування
  const handleEdit = (user: User) => {
    setEditingUser(user);
    dispatch(setCurrentUser(user));
    setIsEditModalVisible(true);
  };

  // Обробка успішного створення
  const handleCreateSuccess = () => {
    setIsCreateModalVisible(false);
    loadUsers();
  };

  // Обробка успішного редагування
  const handleEditSuccess = () => {
    setIsEditModalVisible(false);
    setEditingUser(null);
    loadUsers();
  };

  // Обробка успішної дії (деактивація/активація/скидання пароля)
  const handleActionSuccess = () => {
    loadUsers();
  };

  // Колонки таблиці
  const columns: ColumnsType<User> = [
    {
      title: 'ПІБ',
      dataIndex: 'full_name',
      key: 'full_name',
      sorter: true,
      width: 200,
      render: (text: string, record: User) => (
        <div>
          <div style={{ fontWeight: 500 }}>{text}</div>
          {!record.is_active && (
            <Tag color="red" style={{ marginTop: 4 }}>
              Деактивовано
            </Tag>
          )}
        </div>
      ),
    },
    {
      title: 'Логін',
      dataIndex: 'username',
      key: 'username',
      sorter: true,
      width: 150,
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
      sorter: true,
      width: 200,
      ellipsis: true,
    },
    {
      title: 'Роль',
      dataIndex: 'role',
      key: 'role',
      width: 120,
      render: (role: UserRole) => (
        <Tag color={roleColors[role]}>{roleLabels[role]}</Tag>
      ),
      filters: Object.entries(roleLabels).map(([key, label]) => ({
        text: label,
        value: key,
      })),
    },
    {
      title: 'Статус',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (is_active: boolean) => (
        <Tag color={is_active ? 'success' : 'default'}>
          {is_active ? 'Активний' : 'Неактивний'}
        </Tag>
      ),
      filters: [
        { text: 'Активний', value: true },
        { text: 'Неактивний', value: false },
      ],
    },
    {
      title: 'Створено',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      sorter: true,
      render: (date: string) => dayjs(date).format('DD.MM.YYYY HH:mm'),
    },
    {
      title: 'Дії',
      key: 'actions',
      width: 300,
      fixed: 'right' as const,
      render: (_, record) => (
        <Space size="small" wrap>
          <Tooltip title="Редагувати">
            <Button
              size="small"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            >
              Редагувати
            </Button>
          </Tooltip>

          {record.is_active ? (
            <DeactivateUserButton
              user={record}
              onSuccess={handleActionSuccess}
            />
          ) : (
            <ActivateUserButton
              user={record}
              onSuccess={handleActionSuccess}
            />
          )}

          <ResetPasswordButton
            user={record}
            onSuccess={handleActionSuccess}
          />
        </Space>
      ),
    },
  ];

  // Якщо не має доступу
  if (!hasAccess) {
    return (
      <AuthGuard>
        <MainLayout>
          <div style={{ padding: '24px', textAlign: 'center' }}>
            <Title level={3}>Доступ заборонено</Title>
            <p>Тільки адміністратори мають доступ до цієї сторінки</p>
          </div>
        </MainLayout>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <MainLayout>
        <div style={{ padding: '24px' }}>
          {/* Заголовок та кнопка створення */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 24,
            }}
          >
            <Title level={2} style={{ margin: 0 }}>
              Користувачі
            </Title>
            <Button
              type="primary"
              size="large"
              icon={<UserAddOutlined />}
              onClick={() => setIsCreateModalVisible(true)}
            >
              Створити користувача
            </Button>
          </div>

          {/* Фільтри */}
          <Card style={{ marginBottom: 24 }}>
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12} md={8}>
                <Input
                  placeholder="Пошук за ПІБ, логіном або email..."
                  prefix={<SearchOutlined />}
                  value={filters.search}
                  onChange={(e) =>
                    setFilters((prev) => ({ ...prev, search: e.target.value }))
                  }
                  allowClear
                />
              </Col>
              <Col xs={24} sm={12} md={4}>
                <Select
                  placeholder="Роль"
                  style={{ width: '100%' }}
                  value={filters.role}
                  onChange={(value) =>
                    setFilters((prev) => ({ ...prev, role: value }))
                  }
                  allowClear
                >
                  {Object.entries(roleLabels).map(([key, label]) => (
                    <Option key={key} value={key}>
                      {label}
                    </Option>
                  ))}
                </Select>
              </Col>
              <Col xs={24} sm={12} md={4}>
                <Select
                  placeholder="Статус"
                  style={{ width: '100%' }}
                  value={filters.is_active}
                  onChange={(value) =>
                    setFilters((prev) => ({ ...prev, is_active: value }))
                  }
                  allowClear
                >
                  <Option value={true}>Активний</Option>
                  <Option value={false}>Неактивний</Option>
                </Select>
              </Col>
              <Col xs={24} sm={12} md={4}>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={() => {
                    setFilters({
                      role: undefined,
                      is_active: undefined,
                      search: '',
                    });
                    loadUsers();
                  }}
                  block
                >
                  Очистити фільтри
                </Button>
              </Col>
            </Row>
          </Card>

          {/* Таблиця */}
          <Card>
            <Table
              columns={columns}
              dataSource={users}
              rowKey="id"
              loading={isLoading}
              pagination={{
                ...pagination,
                total,
              }}
              onChange={handleTableChange}
              size="middle"
              scroll={{ x: 1200 }}
            />
          </Card>
        </div>

        {/* Модальні вікна */}
        <CreateUserForm
          visible={isCreateModalVisible}
          onCancel={() => setIsCreateModalVisible(false)}
          onSuccess={handleCreateSuccess}
        />

        <EditUserForm
          visible={isEditModalVisible}
          user={editingUser}
          onCancel={() => {
            setIsEditModalVisible(false);
            setEditingUser(null);
          }}
          onSuccess={handleEditSuccess}
        />
      </MainLayout>
    </AuthGuard>
  );
};

export default UsersPage;
