/**
 * TakeCaseButton Component
 * Кнопка для взяття звернення в роботу (BE-009)
 * Ohmatdyt CRM
 */

import React, { useState } from 'react';
import { Button, message, Modal } from 'antd';
import { CheckCircleOutlined } from '@ant-design/icons';
import api from '@/lib/api';

interface TakeCaseButtonProps {
  caseId: string;
  casePublicId: number;
  currentStatus: string;
  onSuccess: () => void;
}

const TakeCaseButton: React.FC<TakeCaseButtonProps> = ({
  caseId,
  casePublicId,
  currentStatus,
  onSuccess,
}) => {
  const [loading, setLoading] = useState(false);

  // Показуємо кнопку тільки для статусу NEW
  if (currentStatus !== 'NEW') {
    return null;
  }

  const handleTakeCase = () => {
    Modal.confirm({
      title: 'Взяти звернення в роботу?',
      content: `Ви впевнені, що хочете взяти звернення #${casePublicId} в роботу?`,
      okText: 'Так, взяти',
      cancelText: 'Скасувати',
      onOk: async () => {
        setLoading(true);
        try {
          await api.post(`/api/cases/${caseId}/take`);
          message.success('Звернення успішно взято в роботу');
          onSuccess(); // Перезавантажити дані
        } catch (err: any) {
          console.error('Failed to take case:', err);
          const errorMessage = err.response?.data?.detail || 'Помилка при взятті звернення в роботу';
          message.error(errorMessage);
        } finally {
          setLoading(false);
        }
      },
    });
  };

  return (
    <Button
      type="primary"
      icon={<CheckCircleOutlined />}
      onClick={handleTakeCase}
      loading={loading}
      size="large"
    >
      Взяти в роботу
    </Button>
  );
};

export default TakeCaseButton;
