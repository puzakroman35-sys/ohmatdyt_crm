/**
 * Next.js App Component
 * Ohmatdyt CRM
 */

import type { AppProps } from 'next/app';
import { Provider } from 'react-redux';
import { ConfigProvider } from 'antd';
import { useRouter } from 'next/router';
import { store } from '@/store';
import { antdConfig } from '@/config/theme';
import { AuthProvider } from '@/components/Auth';
import MainLayout from '@/components/Layout/MainLayout';
import '@/styles/globals.css';

// Сторінки які не потребують MainLayout
const noLayoutPages = ['/login', '/'];

export default function App({ Component, pageProps }: AppProps) {
  const router = useRouter();
  const isNoLayoutPage = noLayoutPages.includes(router.pathname);

  return (
    <Provider store={store}>
      <AuthProvider>
        <ConfigProvider theme={antdConfig.theme} locale={antdConfig.locale}>
          {isNoLayoutPage ? (
            <Component {...pageProps} />
          ) : (
            <MainLayout>
              <Component {...pageProps} />
            </MainLayout>
          )}
        </ConfigProvider>
      </AuthProvider>
    </Provider>
  );
}
