/**
 * Login Page
 * Ohmatdyt CRM
 */

import React from 'react';
import { Form, Input, Button, Card, Typography, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useRouter } from 'next/router';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import {
  loginStart,
  loginSuccess,
  loginFailure,
  selectAuth,
} from '@/store/slices/authSlice';

const { Title, Text } = Typography;

interface LoginForm {
  email: string;
  password: string;
}

const LoginPage: React.FC = () => {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const { isLoading, error } = useAppSelector(selectAuth);
  const [form] = Form.useForm();

  const onFinish = async (values: LoginForm) => {
    try {
      dispatch(loginStart());
      
      // TODO: Замінити на реальний API запит
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: values.email,
          password: values.password,
        }),
      });

      if (!response.ok) {
        throw new Error('Невірний email або пароль');
      }

      const data = await response.json();
      
      dispatch(
        loginSuccess({
          user: {
            id: data.user.id,
            username: data.user.username,
            email: data.user.email,
            full_name: data.user.full_name,
            role: data.user.role,
            is_active: data.user.is_active,
          },
          accessToken: data.access_token,
          refreshToken: data.refresh_token || '',
        })
      );

      message.success('Успішний вхід!');
      router.push('/dashboard');
    } catch (err: any) {
      dispatch(loginFailure(err.message || 'Помилка входу'));
      message.error(err.message || 'Помилка входу');
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Card
        style={{
          width: 400,
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <Title level={2} style={{ marginBottom: 8 }}>
            Ohmatdyt CRM
          </Title>
          <Text type="secondary">Увійдіть до системи</Text>
        </div>

        <Form
          form={form}
          name="login"
          onFinish={onFinish}
          layout="vertical"
          autoComplete="off"
        >
          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: 'Будь ласка, введіть email!' },
              { type: 'email', message: 'Введіть коректний email!' },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="email@example.com"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="password"
            label="Пароль"
            rules={[{ required: true, message: 'Будь ласка, введіть пароль!' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Пароль"
              size="large"
            />
          </Form.Item>

          {error && (
            <div style={{ color: '#ff4d4f', marginBottom: 16 }}>
              {error}
            </div>
          )}

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              size="large"
              loading={isLoading}
              block
            >
              Увійти
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default LoginPage;
