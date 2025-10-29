/**
 * Dashboard Page
 * Ohmatdyt CRM - FE-301
 * 
 * Дашборд адміністратора з аналітикою та статистикою
 */

import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import { Row, Col, Typography, Spin, message } from 'antd';
import { AuthGuard } from '@/components/Auth';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { selectUser } from '@/store/slices/authSlice';
import {
  StatsSummary,
  StatusDistributionChart,
  OverdueCasesList,
  ExecutorsEfficiencyTable,
  TopCategoriesChart,
  DateRangeFilter,
} from '@/components/Dashboard';
import {
  fetchAllDashboardData,
  selectDashboardSummary,
  selectStatusDistribution,
  selectOverdueCases,
  selectExecutorEfficiency,
  selectCategoriesTop,
  selectSummaryLoading,
  selectStatusDistributionLoading,
  selectOverdueCasesLoading,
  selectExecutorEfficiencyLoading,
  selectCategoriesTopLoading,
  selectSummaryError,
  selectStatusDistributionError,
  selectOverdueCasesError,
  selectExecutorEfficiencyError,
  selectCategoriesTopError,
  selectDateRange,
  selectTopCategoriesLimit,
  setDateRange,
} from '@/store/slices/dashboardSlice';

const { Title } = Typography;

const DashboardPage: React.FC = () => {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const user = useAppSelector(selectUser);

  // Dashboard data
  const summary = useAppSelector(selectDashboardSummary);
  const statusDistribution = useAppSelector(selectStatusDistribution);
  const overdueCases = useAppSelector(selectOverdueCases);
  const executorEfficiency = useAppSelector(selectExecutorEfficiency);
  const categoriesTop = useAppSelector(selectCategoriesTop);

  // Loading states
  const summaryLoading = useAppSelector(selectSummaryLoading);
  const statusDistributionLoading = useAppSelector(selectStatusDistributionLoading);
  const overdueCasesLoading = useAppSelector(selectOverdueCasesLoading);
  const executorEfficiencyLoading = useAppSelector(selectExecutorEfficiencyLoading);
  const categoriesTopLoading = useAppSelector(selectCategoriesTopLoading);

  // Error states
  const summaryError = useAppSelector(selectSummaryError);
  const statusDistributionError = useAppSelector(selectStatusDistributionError);
  const overdueCasesError = useAppSelector(selectOverdueCasesError);
  const executorEfficiencyError = useAppSelector(selectExecutorEfficiencyError);
  const categoriesTopError = useAppSelector(selectCategoriesTopError);

  // Filters
  const dateRange = useAppSelector(selectDateRange);
  const topCategoriesLimit = useAppSelector(selectTopCategoriesLimit);

  useEffect(() => {
    // Якщо не ADMIN - редіректимо на cases
    if (user && user.role !== 'ADMIN') {
      router.replace('/cases');
    }
  }, [user, router]);

  useEffect(() => {
    // Завантажуємо дані при першому рендері
    if (user && user.role === 'ADMIN') {
      loadDashboardData();
    }
  }, [user]);

  const loadDashboardData = async () => {
    try {
      await dispatch(
        fetchAllDashboardData({
          dateRange,
          limit: topCategoriesLimit,
        })
      ).unwrap();
    } catch (error: any) {
      message.error('Помилка завантаження даних дашборду');
    }
  };

  const handleDateRangeApply = () => {
    loadDashboardData();
  };

  // Показуємо loading якщо ще немає інформації про користувача
  if (!user) {
    return (
      <AuthGuard>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          minHeight: '100vh' 
        }}>
          <Spin size="large" tip="Завантаження..." />
        </div>
      </AuthGuard>
    );
  }

  // Якщо не ADMIN, показуємо loading під час редіректу
  if (user.role !== 'ADMIN') {
    return (
      <AuthGuard>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          minHeight: '100vh' 
        }}>
          <Spin size="large" tip="Перенаправлення..." />
        </div>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <Title level={2} style={{ marginBottom: 24 }}>
        📊 Дашборд адміністратора
      </Title>

      {/* Фільтр періоду */}
      <DateRangeFilter
        value={dateRange}
        onChange={(newRange) => dispatch(setDateRange(newRange))}
        onApply={handleDateRangeApply}
      />

      {/* Загальна статистика */}
      <StatsSummary
        data={summary}
        loading={summaryLoading}
        error={summaryError}
      />

      {/* Графіки та аналітика */}
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        {/* Розподіл по статусах */}
        <Col xs={24} lg={12}>
          <StatusDistributionChart
            data={statusDistribution}
            loading={statusDistributionLoading}
            error={statusDistributionError}
          />
        </Col>

        {/* ТОП категорій */}
        <Col xs={24} lg={12}>
          <TopCategoriesChart
            data={categoriesTop}
            loading={categoriesTopLoading}
            error={categoriesTopError}
          />
        </Col>
      </Row>

      {/* Прострочені звернення */}
      <div style={{ marginTop: 24 }}>
        <OverdueCasesList
          data={overdueCases}
          loading={overdueCasesLoading}
          error={overdueCasesError}
        />
      </div>

      {/* Ефективність виконавців */}
      <div style={{ marginTop: 24 }}>
        <ExecutorsEfficiencyTable
          data={executorEfficiency}
          loading={executorEfficiencyLoading}
          error={executorEfficiencyError}
        />
      </div>
    </AuthGuard>
  );
};

export default DashboardPage;
