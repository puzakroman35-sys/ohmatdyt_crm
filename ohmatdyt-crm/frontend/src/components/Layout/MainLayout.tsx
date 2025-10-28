/**
 * Main Layout Component
 * Ohmatdyt CRM
 */

import React, { useState } from 'react';
import { Layout, Menu, Avatar, Dropdown, Typography } from 'antd';
import type { MenuProps } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  DashboardOutlined,
  FileTextOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  BellOutlined,
} from '@ant-design/icons';
import { useRouter } from 'next/router';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { selectUser, logout } from '@/store/slices/authSlice';

const { Header, Sider, Content } = Layout;
const { Text } = Typography;

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const router = useRouter();
  const dispatch = useAppDispatch();
  const user = useAppSelector(selectUser);

  // Меню бічної панелі (динамічне залежно від ролі)
  const sideMenuItems: MenuProps['items'] = [
    // Dashboard тільки для ADMIN
    ...(user?.role === 'ADMIN' ? [{
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: 'Головна',
      onClick: () => router.push('/dashboard'),
    }] : []),
    {
      key: '/cases',
      icon: <FileTextOutlined />,
      label: 'Звернення',
      onClick: () => router.push('/cases'),
    },
    // Адміністрування тільки для ADMIN
    ...(user?.role === 'ADMIN' ? [{
      key: 'admin',
      icon: <SettingOutlined />,
      label: 'Адміністрування',
      children: [
        {
          key: '/admin/users',
          label: 'Користувачі',
          onClick: () => router.push('/admin/users'),
        },
        {
          key: '/admin/categories',
          label: 'Категорії',
          onClick: () => router.push('/admin/categories'),
        },
        {
          key: '/admin/channels',
          label: 'Канали звернень',
          onClick: () => router.push('/admin/channels'),
        },
      ],
    }] : []),
  ];

  // Меню профілю користувача
  const profileMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Профіль',
      onClick: () => router.push('/profile'),
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Вийти',
      onClick: () => {
        dispatch(logout());
        router.push('/login');
      },
    },
  ];

  // Визначаємо активний пункт меню на основі поточного шляху
  const selectedKeys = [router.pathname];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* Бічна панель */}
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        theme="dark"
        width={250}
      >
        {/* Логотип */}
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: collapsed ? 18 : 20,
            fontWeight: 'bold',
            transition: 'all 0.2s',
          }}
        >
          {collapsed ? 'CRM' : 'Ohmatdyt CRM'}
        </div>

        {/* Меню навігації */}
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={selectedKeys}
          items={sideMenuItems}
        />
      </Sider>

      <Layout>
        {/* Верхня панель */}
        <Header
          style={{
            padding: '0 24px',
            background: '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 1px 4px rgba(0,21,41,.08)',
          }}
        >
          {/* Кнопка згортання меню */}
          <div
            style={{ fontSize: 18, cursor: 'pointer' }}
            onClick={() => setCollapsed(!collapsed)}
          >
            {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          </div>

          {/* Права частина header */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
            {/* Сповіщення */}
            <BellOutlined style={{ fontSize: 18, cursor: 'pointer' }} />

            {/* Профіль користувача */}
            <Dropdown menu={{ items: profileMenuItems }} placement="bottomRight">
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                <Avatar
                  icon={<UserOutlined />}
                  style={{ backgroundColor: '#1890ff' }}
                />
                <Text>{user?.full_name || 'Користувач'}</Text>
              </div>
            </Dropdown>
          </div>
        </Header>

        {/* Контентна область */}
        <Content
          style={{
            margin: '24px 16px',
            padding: 24,
            background: '#fff',
            borderRadius: 8,
            minHeight: 280,
          }}
        >
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
