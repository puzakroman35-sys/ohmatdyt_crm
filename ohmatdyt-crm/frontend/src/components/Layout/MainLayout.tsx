/**
 * Main Layout Component
 * Ohmatdyt CRM
 */

import React, { useState, useEffect } from 'react';
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
} from '@ant-design/icons';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { selectUser, logout } from '@/store/slices/authSlice';
import ExecutorCategoryBadge from '@/components/ExecutorCategoryBadge'; // FE-013

const { Header, Sider, Content, Footer } = Layout;
const { Text } = Typography;

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [isClient, setIsClient] = useState(false);
  const router = useRouter();
  const dispatch = useAppDispatch();
  const user = useAppSelector(selectUser);

  // Встановлюємо прапор клієнта для уникнення помилок гідрації
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Меню бічної панелі (динамічне залежно від ролі)
  const sideMenuItems: MenuProps['items'] = [
    // Dashboard тільки для ADMIN - рендеримо тільки на клієнті
    ...(isClient && user?.role === 'ADMIN' ? [{
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: <Link href="/dashboard">Головна</Link>,
    }] : []),
    {
      key: '/cases',
      icon: <FileTextOutlined />,
      label: <Link href="/cases">Звернення</Link>,
    },
    // Адміністрування тільки для ADMIN - рендеримо тільки на клієнті
    ...(isClient && user?.role === 'ADMIN' ? [{
      key: 'admin',
      icon: <SettingOutlined />,
      label: 'Адміністрування',
      children: [
        {
          key: '/users',
          label: <Link href="/users">Користувачі</Link>,
        },
        {
          key: '/admin/categories',
          label: <Link href="/admin/categories">Категорії</Link>,
        },
        {
          key: '/admin/channels',
          label: <Link href="/admin/channels">Канали звернень</Link>,
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
            fontWeight: 'bold',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          {/* Повний логотип */}
          <span
            style={{
              position: 'absolute',
              fontSize: 20,
              opacity: collapsed ? 0 : 1,
              transform: collapsed ? 'scale(0.8)' : 'scale(1)',
              transition: 'opacity 0.3s ease, transform 0.3s ease',
              pointerEvents: collapsed ? 'none' : 'auto',
              whiteSpace: 'nowrap',
            }}
          >
            Ohmatdyt CRM
          </span>
          {/* Скорочений логотип */}
          <span
            style={{
              position: 'absolute',
              fontSize: 18,
              opacity: collapsed ? 1 : 0,
              transform: collapsed ? 'scale(1)' : 'scale(0.8)',
              transition: 'opacity 0.3s ease, transform 0.3s ease',
              pointerEvents: collapsed ? 'auto' : 'none',
            }}
          >
            CRM
          </span>
        </div>

        {/* Меню навігації */}
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={selectedKeys}
          items={sideMenuItems}
        />

        {/* FE-013: Індикатор доступних категорій для EXECUTOR */}
        <div style={{ position: 'absolute', bottom: 60, left: 0, right: 0 }}>
          <ExecutorCategoryBadge />
        </div>
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
            {/* Профіль користувача */}
            <Dropdown menu={{ items: profileMenuItems }} placement="bottomRight">
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                <Avatar
                  icon={<UserOutlined />}
                  style={{ backgroundColor: '#1890ff' }}
                />
                <Text suppressHydrationWarning>
                  {isClient && user ? user.full_name : 'Користувач'}
                </Text>
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

        {/* Футер з копірайтом */}
        <Footer
          style={{
            textAlign: 'center',
            background: '#fff',
            padding: '16px 50px',
            borderTop: '1px solid #f0f0f0',
          }}
          suppressHydrationWarning
        >
          <Text style={{ color: '#8c8c8c', fontSize: 14 }} suppressHydrationWarning>
            © {new Date().getFullYear()} Ohmatdyt CRM. Розроблено{' '}
            <a
              href="https://www.adelina.solutions/"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                color: '#1890ff',
                textDecoration: 'none',
                fontWeight: 500,
              }}
            >
              Adelina Solutions
            </a>
          </Text>
        </Footer>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
