/**
 * Create Case Page
 * Сторінка створення звернення
 * Ohmatdyt CRM - FE-003
 */

import React from 'react';
import { useRouter } from 'next/router';
import { Card } from 'antd';
import MainLayout from '@/components/Layout/MainLayout';
import { AuthGuard, RoleGuard } from '@/components/Auth';
import CreateCaseForm from '@/components/Cases/CreateCaseForm';

const CreateCasePage: React.FC = () => {
  const router = useRouter();

  // Обробка успішного створення звернення
  const handleSuccess = (caseData: any) => {
    // Перенаправляємо на сторінку зі списком звернень
    router.push('/cases');
  };

  // Обробка скасування
  const handleCancel = () => {
    router.push('/cases');
  };

  return (
    <AuthGuard>
      <RoleGuard allowedRoles={['OPERATOR', 'ADMIN']}>
        <MainLayout>
          <div style={{ padding: '24px' }}>
            <Card>
              <CreateCaseForm
                onSuccess={handleSuccess}
                onCancel={handleCancel}
              />
            </Card>
          </div>
        </MainLayout>
      </RoleGuard>
    </AuthGuard>
  );
};

export default CreateCasePage;
