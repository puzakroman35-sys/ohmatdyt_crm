/**
 * Profile Page
 * FE-014: Сторінка профілю користувача з можливістю зміни пароля
 * Ohmatdyt CRM
 */

import React from 'react';
import { Row, Col, Typography, Space } from 'antd';
import { UserOutlined } from '@ant-design/icons';
import { AuthGuard } from '@/components/Auth';
import { ProfileInfo, ChangePasswordForm } from '@/components/Profile';
import { useAppSelector } from '@/store/hooks';
import { selectUser } from '@/store/slices/authSlice';

const { Title } = Typography;

/**
 * Сторінка профілю користувача
 * MainLayout вже застосовується в _app.tsx
 */
const ProfilePage: React.FC = () => {
  const user = useAppSelector(selectUser);

  if (!user) {
    return null;
  }

  return (
    <AuthGuard>
      {/* Заголовок сторінки */}
      <Space style={{ marginBottom: 24 }}>
        <UserOutlined style={{ fontSize: 32, color: '#1890ff' }} />
        <Title level={2} style={{ margin: 0 }}>
          Профіль користувача
        </Title>
      </Space>

      {/* Контент профілю - одна колонка */}
      <Row gutter={[24, 24]}>
        <Col xs={24}>
          {/* Інформація про користувача зверху */}
          <ProfileInfo user={user} />
        </Col>

        <Col xs={24} lg={12}>
          {/* Форма зміни пароля знизу - 50% ширини на великих екранах */}
          <ChangePasswordForm />
        </Col>
      </Row>
    </AuthGuard>
  );
};

export default ProfilePage;
