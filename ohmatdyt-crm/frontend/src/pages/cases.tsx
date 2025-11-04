/**
 * Cases List Page
 * Ohmatdyt CRM
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
  DatePicker,
  Input,
  Row,
  Col,
  message,
  Spin,
  Popconfirm,
} from 'antd';
import {
  SearchOutlined,
  FilterOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { useRouter } from 'next/router';
import dayjs from 'dayjs';
import { AuthGuard } from '@/components/Auth';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import {
  fetchCasesAsync,
  takeCaseAsync,
  selectCases,
  selectCasesLoading,
  selectCasesError,
  selectCasesTotal,
  Case,
  CaseStatus,
  Category,
} from '@/store/slices/casesSlice';
import { selectUser } from '@/store/slices/authSlice';
import api from '@/lib/api';

const { Title } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

// Статуси з українськими назвами
const statusLabels: Record<CaseStatus, string> = {
  NEW: 'Новий',
  IN_PROGRESS: 'В роботі',
  NEEDS_INFO: 'Потрібна інформація',
  REJECTED: 'Відхилено',
  DONE: 'Виконано',
};

// Кольори для статусів
const statusColors: Record<CaseStatus, string> = {
  NEW: 'blue',
  IN_PROGRESS: 'orange',
  NEEDS_INFO: 'red',
  REJECTED: 'red',
  DONE: 'green',
};

const CasesPage: React.FC = () => {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const user = useAppSelector(selectUser);
  const cases = useAppSelector(selectCases);
  const isLoading = useAppSelector(selectCasesLoading);
  const error = useAppSelector(selectCasesError);
  const total = useAppSelector(selectCasesTotal);

  // FE-013: Список категорій для фільтру (враховує доступи для EXECUTOR)
  const [categories, setCategories] = useState<Category[]>([]);
  const [loadingCategories, setLoadingCategories] = useState(false);
  const [hasNoAccess, setHasNoAccess] = useState(false); // FE-013: Чи немає доступів до категорій

  // Стан фільтрів
  const [filters, setFilters] = useState({
    status: undefined as CaseStatus | undefined,
    category_id: undefined as string | undefined,
    channel_id: undefined as string | undefined,
    dateRange: undefined as [dayjs.Dayjs, dayjs.Dayjs] | undefined,
    search: '',
    overdue: undefined as boolean | undefined,
  });

  // Стан пагінації
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total: number, range: [number, number]) =>
      `${range[0]}-${range[1]} з ${total} звернень`,
  });

  // Стан сортування
  const [sorter, setSorter] = useState({
    field: 'created_at',
    order: 'descend' as 'ascend' | 'descend',
  });

  // FE-013: Завантаження категорій з урахуванням доступів для EXECUTOR
  useEffect(() => {
    const fetchCategories = async () => {
      if (!user) return;

      setLoadingCategories(true);
      setHasNoAccess(false);

      try {
        // FE-013: Для EXECUTOR отримуємо доступні категорії через /users/me/category-access
        if (user.role === 'EXECUTOR') {
          const accessResponse = await api.get('/api/users/me/category-access');
          const accessData = accessResponse.data;

          if (accessData.total === 0) {
            // Немає доступів до жодної категорії
            setCategories([]);
            setHasNoAccess(true);
          } else {
            // Маємо доступ до певних категорій - завантажуємо деталі
            const categoryIds = accessData.categories.map((c: any) => c.category_id);
            
            // Отримуємо повну інформацію про категорії
            const categoriesResponse = await api.get('/api/categories', {
              params: { is_active: true }
            });

            const allCategories = Array.isArray(categoriesResponse.data)
              ? categoriesResponse.data
              : categoriesResponse.data.categories || [];

            // Фільтруємо тільки доступні категорії
            const accessibleCategories = allCategories.filter((cat: Category) =>
              categoryIds.includes(cat.id)
            );

            setCategories(accessibleCategories);
            setHasNoAccess(false);
          }
        } else {
          // Для ADMIN та OPERATOR показуємо всі категорії
          const response = await api.get('/api/categories', {
            params: { is_active: true }
          });
          
          const data = response.data;
          if (Array.isArray(data)) {
            setCategories(data);
          } else if (data && Array.isArray(data.categories)) {
            setCategories(data.categories);
          } else {
            console.warn('Unexpected categories response format:', data);
            setCategories([]);
          }
          setHasNoAccess(false);
        }
      } catch (err) {
        console.error('Failed to load categories:', err);
        message.error('Помилка завантаження категорій');
        setCategories([]);
        setHasNoAccess(false);
      } finally {
        setLoadingCategories(false);
      }
    };

    fetchCategories();
  }, [user]);

  // Завантаження даних
  const loadCases = () => {
    if (!user) return;

    // Визначення endpoint залежно від ролі
    let endpoint = '/api/cases';
    if (user.role === 'OPERATOR') {
      endpoint = '/api/cases/my';
    } else if (user.role === 'EXECUTOR') {
      endpoint = '/api/cases/assigned';
    }

    // Побудова фільтрів
    const apiFilters: Record<string, any> = {};
    if (filters.status) apiFilters.status = filters.status;
    if (filters.category_id) apiFilters.category_id = filters.category_id;
    if (filters.channel_id) apiFilters.channel_id = filters.channel_id;
    if (filters.overdue !== undefined) apiFilters.overdue = filters.overdue;
    if (filters.dateRange) {
      apiFilters.date_from = filters.dateRange[0].format('YYYY-MM-DD');
      apiFilters.date_to = filters.dateRange[1].format('YYYY-MM-DD');
    }
    if (filters.search) apiFilters.search = filters.search;

    // Побудова сортування
    const sort = {
      field: sorter.field,
      order: sorter.order === 'descend' ? 'desc' : 'asc' as 'asc' | 'desc',
    };

    dispatch(fetchCasesAsync({
      endpoint,
      filters: apiFilters,
      pagination: {
        skip: (pagination.current - 1) * pagination.pageSize,
        limit: pagination.pageSize,
      },
      sort,
    }));
  };

  // Завантаження при монтажі та зміні фільтрів
  useEffect(() => {
    if (user) {
      loadCases();
    }
  }, [user, pagination.current, pagination.pageSize, sorter, filters]);

  // Автооновлення кожні 30 секунд
  useEffect(() => {
    if (!user) return;

    const interval = setInterval(() => {
      loadCases();
    }, 30000); // 30 секунд

    return () => clearInterval(interval);
  }, [user, pagination.current, pagination.pageSize, sorter, filters]);

  // Обробка зміни пагінації
  const handleTableChange = (pagination: any, filters: any, sorter: any) => {
    setPagination(prev => ({
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

  // Обробка кліку на рядок
  const handleRowClick = (record: Case) => {
    router.push(`/cases/${record.id}`);
  };

  // Обробка "Взяти в роботу"
  const handleTakeCase = async (caseId: string, event: React.MouseEvent) => {
    event.stopPropagation(); // Запобігти навігації до деталей
    
    try {
      await dispatch(takeCaseAsync(caseId)).unwrap();
      message.success('Звернення взято в роботу');
      loadCases(); // Оновити список
    } catch (err: any) {
      message.error(err || 'Помилка при взятті звернення в роботу');
    }
  };

  // Колонки таблиці
  const columns: ColumnsType<Case> = [
    {
      title: 'ID',
      dataIndex: 'public_id',
      key: 'public_id',
      width: 100,
      sorter: true,
      render: (public_id: number) => (
        <span style={{ fontWeight: 'bold', color: '#1890ff' }}>
          #{public_id}
        </span>
      ),
    },
    {
      title: 'Дата створення',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      sorter: true,
      render: (date: string) => dayjs(date).format('DD.MM.YYYY HH:mm'),
    },
    {
      title: 'Заявник',
      dataIndex: 'applicant_name',
      key: 'applicant_name',
      ellipsis: true,
    },
    {
      title: 'Категорія',
      dataIndex: 'category',
      key: 'category',
      render: (category: any) => category?.name || 'Невідомо',
    },
    {
      title: 'Канал',
      dataIndex: 'channel',
      key: 'channel',
      render: (channel: any) => channel?.name || 'Невідомо',
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      width: 150,
      render: (status: CaseStatus) => (
        <Tag color={statusColors[status]}>
          {statusLabels[status]}
        </Tag>
      ),
    },
    {
      title: 'Відповідальний',
      dataIndex: 'responsible',
      key: 'responsible',
      render: (responsible: any) => responsible?.full_name || 'Не призначено',
    },
  ];

  // Додати колонку "Дії" для виконавців
  if (user?.role === 'EXECUTOR') {
    columns.push({
      title: 'Дії',
      key: 'actions',
      width: 120,
      render: (_, record) => {
        // Показуємо кнопку "Взяти в роботу" тільки для звернень зі статусом NEW
        if (record.status === CaseStatus.NEW && !record.responsible_id) {
          return (
            <Popconfirm
              title="Взяти звернення в роботу?"
              description="Ви станете відповідальним за це звернення"
              onConfirm={(e) => handleTakeCase(record.id, e as any)}
              okText="Так"
              cancelText="Ні"
              onCancel={(e) => e?.stopPropagation()}
            >
              <Button
                type="primary"
                size="small"
                icon={<CheckCircleOutlined />}
                onClick={(e) => e.stopPropagation()}
              >
                Взяти
              </Button>
            </Popconfirm>
          );
        }
        return null;
      },
    });
  }

  // Перевірка чи прострочено звернення (більше 7 днів)
  const isOverdue = (createdAt: string, status: CaseStatus) => {
    if (status === 'DONE' || status === 'REJECTED') return false;
    const daysDiff = dayjs().diff(dayjs(createdAt), 'day');
    return daysDiff > 7;
  };

  // Рядки з підсвіткою
  const getRowClassName = (record: Case) => {
    return isOverdue(record.created_at, record.status) ? 'overdue-row' : '';
  };

  return (
    <AuthGuard>
      <div style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <Title level={2} style={{ margin: 0 }}>
            Звернення
          </Title>
          <Button
            type="primary"
            size="large"
            onClick={() => router.push('/cases/create')}
          >
            + Створити звернення
          </Button>
        </div>

        {/* FE-013: Повідомлення про відсутність доступів до категорій для EXECUTOR */}
        {hasNoAccess && user?.role === 'EXECUTOR' && (
          <Card style={{ marginBottom: 24, borderColor: '#ff4d4f' }}>
            <div style={{ textAlign: 'center', padding: '24px' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>⚠️</div>
              <Title level={3} style={{ color: '#ff4d4f', marginBottom: '8px' }}>
                У вас немає доступу до категорій
              </Title>
              <p style={{ fontSize: '16px', color: '#666', marginBottom: 0 }}>
                Зверніться до адміністратора для надання доступу до категорій звернень.
                <br />
                Без доступу до категорій ви не зможете переглядати та обробляти звернення.
              </p>
            </div>
          </Card>
        )}

        {/* Фільтри */}
        <Card style={{ marginBottom: 24 }}>
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} md={6}>
              <Input
                placeholder="Пошук за іменем або ID..."
                prefix={<SearchOutlined />}
                value={filters.search}
                onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                allowClear
              />
            </Col>
            <Col xs={24} sm={12} md={4}>
              <Select
                placeholder="Статус"
                style={{ width: '100%' }}
                value={filters.status}
                onChange={(value) => setFilters(prev => ({ ...prev, status: value }))}
                allowClear
              >
                {Object.entries(statusLabels).map(([key, label]) => (
                  <Option key={key} value={key}>{label}</Option>
                ))}
              </Select>
            </Col>
            <Col xs={24} sm={12} md={5}>
              <Select
                placeholder="Категорія"
                style={{ width: '100%' }}
                value={filters.category_id}
                onChange={(value) => setFilters(prev => ({ ...prev, category_id: value }))}
                allowClear
                loading={loadingCategories}
                showSearch
                optionFilterProp="children"
              >
                {categories.map((cat) => (
                  <Option key={cat.id} value={cat.id}>{cat.name}</Option>
                ))}
              </Select>
            </Col>
            <Col xs={24} sm={12} md={5}>
              <RangePicker
                placeholder={['Дата від', 'Дата до']}
                style={{ width: '100%' }}
                value={filters.dateRange}
                onChange={(dates) => setFilters(prev => ({ ...prev, dateRange: dates as any }))}
                format="DD.MM.YYYY"
              />
            </Col>
            <Col xs={24} sm={12} md={4}>
              <Select
                placeholder="Прострочені"
                style={{ width: '100%' }}
                value={filters.overdue}
                onChange={(value) => setFilters(prev => ({ ...prev, overdue: value }))}
                allowClear
              >
                <Option value={true}>Так</Option>
                <Option value={false}>Ні</Option>
              </Select>
            </Col>
          </Row>
          <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
            <Col>
              <Space>
                <Button
                  icon={<FilterOutlined />}
                  onClick={() => loadCases()}
                >
                  Фільтрувати
                </Button>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={() => {
                    setFilters({
                      status: undefined,
                      category_id: undefined,
                      channel_id: undefined,
                      dateRange: undefined,
                      search: '',
                      overdue: undefined,
                    });
                    loadCases();
                  }}
                >
                  Очистити
                </Button>
              </Space>
            </Col>
          </Row>
        </Card>

        {/* Таблиця */}
        <Card>
          <Table
            columns={columns}
            dataSource={cases}
            rowKey="id"
            loading={isLoading}
            pagination={{
              ...pagination,
              total,
            }}
            onChange={handleTableChange}
            onRow={(record) => ({
              onClick: () => handleRowClick(record),
              style: { cursor: 'pointer' },
            })}
            rowClassName={getRowClassName}
            size="middle"
            scroll={{ x: 800 }}
          />
        </Card>

        {/* Повідомлення про помилку */}
        {error && (
          <div style={{ marginTop: 16, color: '#ff4d4f' }}>
            Помилка: {error}
          </div>
        )}
      </div>

      <style jsx>{`
        .overdue-row {
          background-color: #fff2f0 !important;
          border-left: 3px solid #ff4d4f;
        }
        .overdue-row:hover {
          background-color: #ffe7e6 !important;
        }
      `}</style>
    </AuthGuard>
  );
};

export default CasesPage;