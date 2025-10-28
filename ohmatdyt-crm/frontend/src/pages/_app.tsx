/**
 * Next.js App Component
 * Ohmatdyt CRM
 */

import type { AppProps } from 'next/app';
import { Provider } from 'react-redux';
import { ConfigProvider } from 'antd';
import { store } from '@/store';
import { antdConfig } from '@/config/theme';
import { AuthProvider } from '@/components/Auth';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <Provider store={store}>
      <AuthProvider>
        <ConfigProvider theme={antdConfig.theme} locale={antdConfig.locale}>
          <Component {...pageProps} />
        </ConfigProvider>
      </AuthProvider>
    </Provider>
  );
}
