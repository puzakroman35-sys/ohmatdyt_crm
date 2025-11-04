/**
 * ExecutorCategoryBadge Component
 * FE-013: Індикатор доступних категорій для виконавця
 * Ohmatdyt CRM
 */

import React, { useEffect, useState } from 'react';
import { Badge, Tooltip, Space, Typography } from 'antd';
import { TagsOutlined } from '@ant-design/icons';
import api from '@/lib/api';
import { useAppSelector } from '@/store/hooks';
import { selectUser } from '@/store/slices/authSlice';

const { Text } = Typography;

interface CategoryAccess {
  id: string;
  category_id: string;
  category_name: string;
}

const ExecutorCategoryBadge: React.FC = () => {
  const user = useAppSelector(selectUser);
  const [categories, setCategories] = useState<CategoryAccess[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchCategoryAccess = async () => {
      // Показуємо тільки для EXECUTOR
      if (!user || user.role !== 'EXECUTOR') return;

      setLoading(true);
      try {
        const response = await api.get('/api/users/me/category-access');
        setCategories(response.data.categories || []);
      } catch (err) {
        console.error('Failed to load category access:', err);
        setCategories([]);
      } finally {
        setLoading(false);
      }
    };

    fetchCategoryAccess();
  }, [user]);

  // Не показуємо компонент якщо не EXECUTOR
  if (!user || user.role !== 'EXECUTOR') {
    return null;
  }

  // Формуємо tooltip контент зі списком категорій
  const tooltipContent = categories.length > 0 ? (
    <div>
      <Text strong style={{ color: '#fff', display: 'block', marginBottom: 8 }}>
        Доступні категорії:
      </Text>
      {categories.map((cat) => (
        <div key={cat.id} style={{ color: '#fff', marginBottom: 4 }}>
          • {cat.category_name}
        </div>
      ))}
    </div>
  ) : (
    <Text style={{ color: '#fff' }}>Немає доступу до категорій</Text>
  );

  return (
    <Tooltip title={tooltipContent} placement="right">
      <Space
        style={{
          padding: '8px 16px',
          cursor: 'pointer',
          borderRadius: '4px',
          transition: 'background-color 0.3s',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'transparent';
        }}
      >
        <TagsOutlined style={{ fontSize: '16px', color: '#fff' }} />
        <Badge
          count={categories.length}
          showZero
          style={{
            backgroundColor: categories.length > 0 ? '#52c41a' : '#ff4d4f',
          }}
        >
          <Text style={{ color: '#fff', marginRight: 8 }}>
            Категорії
          </Text>
        </Badge>
      </Space>
    </Tooltip>
  );
};

export default ExecutorCategoryBadge;
