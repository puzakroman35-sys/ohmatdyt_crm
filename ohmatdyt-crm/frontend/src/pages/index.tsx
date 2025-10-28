import React, { useEffect, useState } from 'react';
import Head from 'next/head';

interface ApiResponse {
  message: string;
  version: string;
  environment: string;
}

const HomePage: React.FC = () => {
  const [apiStatus, setApiStatus] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/')
      .then((res) => res.json())
      .then((data) => {
        setApiStatus(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <>
      <Head>
        <title>Ohmatdyt CRM</title>
        <meta name="description" content="CRM system for Ohmatdyt hospital" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      
      <div style={styles.container}>
        <main style={styles.main}>
          <h1 style={styles.title}>Ohmatdyt CRM</h1>
          <p style={styles.description}>
            Welcome to the Ohmatdyt Hospital CRM System
          </p>
          
          <div style={styles.card}>
            <h2>API Status</h2>
            {loading && <p>Loading...</p>}
            {error && <p style={styles.error}>Error: {error}</p>}
            {apiStatus && (
              <div>
                <p><strong>Message:</strong> {apiStatus.message}</p>
                <p><strong>Version:</strong> {apiStatus.version}</p>
                <p><strong>Environment:</strong> {apiStatus.environment}</p>
              </div>
            )}
          </div>

          <div style={styles.grid}>
            <div style={styles.card}>
              <h3>Patients &rarr;</h3>
              <p>Manage patient records and medical history</p>
            </div>

            <div style={styles.card}>
              <h3>Appointments &rarr;</h3>
              <p>Schedule and manage appointments</p>
            </div>

            <div style={styles.card}>
              <h3>Doctors &rarr;</h3>
              <p>Manage medical staff and schedules</p>
            </div>

            <div style={styles.card}>
              <h3>Reports &rarr;</h3>
              <p>View analytics and generate reports</p>
            </div>
          </div>
        </main>
      </div>
    </>
  );
};

const styles = {
  container: {
    minHeight: '100vh',
    padding: '0 0.5rem',
    display: 'flex',
    flexDirection: 'column' as const,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  main: {
    padding: '5rem 0',
    flex: 1,
    display: 'flex',
    flexDirection: 'column' as const,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    margin: 0,
    lineHeight: 1.15,
    fontSize: '4rem',
    textAlign: 'center' as const,
    color: '#0070f3',
  },
  description: {
    textAlign: 'center' as const,
    lineHeight: 1.5,
    fontSize: '1.5rem',
    marginBottom: '2rem',
  },
  grid: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexWrap: 'wrap' as const,
    maxWidth: '800px',
    marginTop: '3rem',
  },
  card: {
    margin: '1rem',
    padding: '1.5rem',
    textAlign: 'left' as const,
    color: 'inherit',
    textDecoration: 'none',
    border: '1px solid #eaeaea',
    borderRadius: '10px',
    transition: 'color 0.15s ease, border-color 0.15s ease',
    maxWidth: '300px',
    backgroundColor: 'white',
  },
  error: {
    color: 'red',
  },
};

export default HomePage;