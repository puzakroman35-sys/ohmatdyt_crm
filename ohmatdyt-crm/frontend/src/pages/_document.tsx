/**
 * Next.js Document Component
 * Ohmatdyt CRM
 */

import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="uk">
      <Head>
        <link rel="icon" href="/favicon.ico" />
        <meta name="description" content="Ohmatdyt CRM - Система управління зверненнями" />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
