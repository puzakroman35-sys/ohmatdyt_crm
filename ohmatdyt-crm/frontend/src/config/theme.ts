/**
 * Ant Design Theme Configuration
 * Ohmatdyt CRM
 */

import type { ThemeConfig } from 'antd';
import ukUA from 'antd/locale/uk_UA';

// Кастомна тема для Ohmatdyt CRM
export const theme: ThemeConfig = {
  token: {
    // Головні кольори
    colorPrimary: '#1890ff',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#ff4d4f',
    colorInfo: '#1890ff',
    
    // Типографія
    fontSize: 14,
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    
    // Відступи та розміри
    borderRadius: 6,
    
    // Заголовки
    fontSizeHeading1: 38,
    fontSizeHeading2: 30,
    fontSizeHeading3: 24,
    fontSizeHeading4: 20,
    fontSizeHeading5: 16,
  },
  
  components: {
    // Налаштування Layout
    Layout: {
      headerBg: '#001529',
      headerPadding: '0 24px',
      headerHeight: 64,
      siderBg: '#001529',
    },
    
    // Налаштування Menu
    Menu: {
      darkItemBg: '#001529',
      darkSubMenuItemBg: '#000c17',
      darkItemSelectedBg: '#1890ff',
    },
    
    // Налаштування Button
    Button: {
      controlHeight: 32,
      borderRadius: 6,
    },
    
    // Налаштування Input
    Input: {
      controlHeight: 32,
      borderRadius: 6,
    },
    
    // Налаштування Select
    Select: {
      controlHeight: 32,
      borderRadius: 6,
    },
    
    // Налаштування Table
    Table: {
      headerBg: '#fafafa',
      headerColor: 'rgba(0, 0, 0, 0.88)',
      rowHoverBg: '#f5f5f5',
    },
    
    // Налаштування Card
    Card: {
      borderRadius: 8,
    },
  },
};

// Українська локаль
export const locale = ukUA;

// Налаштування для ConfigProvider
export const antdConfig = {
  theme,
  locale,
};
