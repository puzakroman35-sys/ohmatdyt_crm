/**
 * Categories Page
 * Ohmatdyt CRM - Управління категоріями (тільки для ADMIN)
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
import { AuthGuard } from '@/components/Auth';
import { AppDispatch } from '@/store';
import {
  fetchCategoriesAsync,
  selectCategories,
  selectCategoriesTotal,
  selectCategoriesLoading,
  Category,
} from '@/store/slices/categoriesSlice';
import { selectUser } from '@/store/slices/authSlice';
import {
  CreateCategoryForm,
  EditCategoryForm,
  DeactivateCategoryButton,
  ActivateCategoryButton,
} from '@/components/Categories';
import dayjs from 'dayjs';

const { Title } = Typography;

const CategoriesPage: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const categories = useSelector(selectCategories);
  const total = useSelector(selectCategoriesTotal);
  const isLoading = useSelector(selectCategoriesLoading);
  const user = useSelector(selectUser);

  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);

  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
  });
  const [searchText, setSearchText] = useState('');
  const [includeInactive, setIncludeInactive] = useState(true);

  // Завантаження даних
  const loadData = () => {
    dispatch(
      fetchCategoriesAsync({
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

  const handleEdit = (category: Category) => {
    setSelectedCategory(category);
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
        <Alert
          message="Доступ заборонено"
          description="Тільки адміністратори мають доступ до управління категоріями."
          type="error"
          showIcon
        />
      </AuthGuard>
    );
  }

  // Колонки таблиці
  const columns: ColumnsType<Category> = [
    {
      title: 'Назва категорії',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: Category) => (
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
          {isActive ? 'Активна' : 'Неактивна'}
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
      render: (_, record: Category) => (
        <Space size="small" wrap>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Редагувати
          </Button>
          <DeactivateCategoryButton
            category={record}
            onSuccess={handleActionSuccess}
          />
          <ActivateCategoryButton
            category={record}
            onSuccess={handleActionSuccess}
          />
        </Space>
      ),
    },
  ];

  return (
    <AuthGuard>
      <div style={{ padding: '24px' }}>
        <Card>
            <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
              <Col>
                <Title level={2} style={{ margin: 0 }}>
                  Управління категоріями
                </Title>
              </Col>
              <Col>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  size="large"
                  onClick={() => setCreateModalVisible(true)}
                >
                  Створити категорію
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
          dataSource={categories || []}
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
      <CreateCategoryForm
        visible={createModalVisible}
        onClose={() => setCreateModalVisible(false)}
        onSuccess={handleActionSuccess}
      />

      <EditCategoryForm
        visible={editModalVisible}
        category={selectedCategory}
        onClose={() => {
          setEditModalVisible(false);
          setSelectedCategory(null);
        }}
        onSuccess={handleActionSuccess}
      />
      </div>
    </AuthGuard>
  );
};

export default CategoriesPage;
