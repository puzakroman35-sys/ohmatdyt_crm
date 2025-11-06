/**
 * ProfileInfo Component
 * FE-014: Відображення інформації про користувача
 * Ohmatdyt CRM
 */

import React, { useEffect, useState } from 'react';
import { Card, Descriptions, Tag, Typography, Space, Alert } from 'antd';
import {
  UserOutlined,
  MailOutlined,
  IdcardOutlined,
  SafetyOutlined,
  CalendarOutlined,
  TagsOutlined,
} from '@ant-design/icons';
import api from '@/lib/api';
import { User } from '@/store/slices/authSlice';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

interface CategoryAccess {
  id: string;
  category_id: string;
  category_name: string;
}

interface ProfileInfoProps {
  user: User;
}

const ProfileInfo: React.FC<ProfileInfoProps> = ({ user }) => {
  const [categories, setCategories] = useState<CategoryAccess[]>([]);
  const [loadingCategories, setLoadingCategories] = useState(false);

  // Завантаження категорій для EXECUTOR
  useEffect(() => {
    const fetchCategories = async () => {
      if (user.role !== 'EXECUTOR') return;

      setLoadingCategories(true);
      try {
        const response = await api.get('/api/users/me/category-access');
        setCategories(response.data.categories || []);
      } catch (err) {
        console.error('Failed to load categories:', err);
        setCategories([]);
      } finally {
        setLoadingCategories(false);
      }
    };

    fetchCategories();
  }, [user.role]);

  // Визначення кольору для ролі
  const getRoleColor = (role: string) => {
    switch (role) {
      case 'ADMIN':
        return 'red';
      case 'OPERATOR':
        return 'blue';
      case 'EXECUTOR':
        return 'green';
      default:
        return 'default';
    }
  };

  // Визначення тексту ролі
  const getRoleText = (role: string) => {
    switch (role) {
      case 'ADMIN':
        return 'Адміністратор';
      case 'OPERATOR':
        return 'Оператор';
      case 'EXECUTOR':
        return 'Виконавець';
      default:
        return role;
    }
  };

  return (
    <Card
      title={
        <Space>
          <UserOutlined />
          <Title level={4} style={{ margin: 0 }}>
            Інформація про користувача
          </Title>
        </Space>
      }
      bordered={false}
      style={{ marginBottom: 24 }}
    >
      <Descriptions column={1} bordered>
        <Descriptions.Item
          label={
            <Space>
              <IdcardOutlined />
              <Text strong>ПІБ</Text>
            </Space>
          }
        >
          {user.full_name}
        </Descriptions.Item>

        <Descriptions.Item
          label={
            <Space>
              <UserOutlined />
              <Text strong>Ім'я користувача</Text>
            </Space>
          }
        >
          {user.username}
        </Descriptions.Item>

        <Descriptions.Item
          label={
            <Space>
              <MailOutlined />
              <Text strong>Email</Text>
            </Space>
          }
        >
          {user.email}
        </Descriptions.Item>

        <Descriptions.Item
          label={
            <Space>
              <SafetyOutlined />
              <Text strong>Роль</Text>
            </Space>
          }
        >
          <Tag color={getRoleColor(user.role)}>{getRoleText(user.role)}</Tag>
        </Descriptions.Item>

        <Descriptions.Item
          label={
            <Space>
              <SafetyOutlined />
              <Text strong>Статус</Text>
            </Space>
          }
        >
          <Tag color={user.is_active ? 'success' : 'error'}>
            {user.is_active ? 'Активний' : 'Неактивний'}
          </Tag>
        </Descriptions.Item>

        {user.role === 'EXECUTOR' && (
          <Descriptions.Item
            label={
              <Space>
                <TagsOutlined />
                <Text strong>Доступні категорії</Text>
              </Space>
            }
          >
            {loadingCategories ? (
              <Text type="secondary">Завантаження...</Text>
            ) : categories.length > 0 ? (
              <Space wrap>
                {categories.map((cat) => (
                  <Tag key={cat.id} color="blue">
                    {cat.category_name}
                  </Tag>
                ))}
              </Space>
            ) : (
              <Alert
                message="Немає доступних категорій"
                type="warning"
                showIcon
                style={{ marginTop: 8 }}
              />
            )}
          </Descriptions.Item>
        )}
      </Descriptions>
    </Card>
  );
};

export default ProfileInfo;
