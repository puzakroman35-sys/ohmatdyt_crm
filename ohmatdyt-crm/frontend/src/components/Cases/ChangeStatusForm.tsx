/**
 * ChangeStatusForm Component
 * Форма для зміни статусу звернення з обов'язковим коментарем (BE-010)
 * Ohmatdyt CRM
 */

import React, { useState } from 'react';
import { Button, Modal, Form, Select, Input, message, Space, Alert } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import api from '@/lib/api';

const { TextArea } = Input;
const { Option } = Select;

interface ChangeStatusFormProps {
  caseId: string;
  casePublicId: number;
  currentStatus: string;
  userRole?: 'OPERATOR' | 'EXECUTOR' | 'ADMIN';
  onSuccess: () => void;
}

// Можливі переходи статусів для EXECUTOR
const executorStatusTransitions: Record<string, Array<{ value: string; label: string; color: string }>> = {
  IN_PROGRESS: [
    { value: 'NEEDS_INFO', label: 'Потрібна інформація', color: 'red' },
    { value: 'REJECTED', label: 'Відхилено', color: 'red' },
    { value: 'DONE', label: 'Виконано', color: 'green' },
  ],
  NEEDS_INFO: [
    { value: 'IN_PROGRESS', label: 'В роботі', color: 'orange' },
    { value: 'REJECTED', label: 'Відхилено', color: 'red' },
    { value: 'DONE', label: 'Виконано', color: 'green' },
  ],
};

// FE-011: Всі можливі статуси для ADMIN (без обмежень)
const allStatuses: Array<{ value: string; label: string; color: string }> = [
  { value: 'NEW', label: 'Новий', color: 'blue' },
  { value: 'IN_PROGRESS', label: 'В роботі', color: 'orange' },
  { value: 'NEEDS_INFO', label: 'Потрібна інформація', color: 'red' },
  { value: 'REJECTED', label: 'Відхилено', color: 'red' },
  { value: 'DONE', label: 'Виконано', color: 'green' },
];

const ChangeStatusForm: React.FC<ChangeStatusFormProps> = ({
  caseId,
  casePublicId,
  currentStatus,
  userRole,
  onSuccess,
}) => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  // FE-011: ADMIN має доступ до всіх статусів, EXECUTOR - обмежені переходи
  const isAdmin = userRole === 'ADMIN';
  const availableStatuses = isAdmin
    ? allStatuses.filter((s) => s.value !== currentStatus) // ADMIN бачить всі, крім поточного
    : executorStatusTransitions[currentStatus] || [];

  // Показуємо кнопку тільки якщо є доступні переходи
  if (availableStatuses.length === 0) {
    return null;
  }

  const showModal = () => {
    setIsModalVisible(true);
  };

  const handleCancel = () => {
    setIsModalVisible(false);
    form.resetFields();
  };

  const handleSubmit = async (values: { new_status: string; comment: string }) => {
    setLoading(true);
    try {
      await api.post(`/api/cases/${caseId}/status`, {
        to_status: values.new_status,
        comment: values.comment,
      });

      message.success('Статус звернення успішно змінено');
      setIsModalVisible(false);
      form.resetFields();
      onSuccess(); // Перезавантажити дані
    } catch (err: any) {
      console.error('Failed to change status:', err);
      
      // FE-013: Обробка помилки 403 - немає доступу до категорії звернення
      if (err.response?.status === 403) {
        message.error('У вас немає доступу до категорії цього звернення');
      } else {
        const errorMessage = err.response?.data?.detail || 'Помилка при зміні статусу';
        message.error(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Button
        type="default"
        icon={<EditOutlined />}
        onClick={showModal}
        size="large"
      >
        Змінити статус
      </Button>

      <Modal
        title={`Зміна статусу звернення #${casePublicId}`}
        open={isModalVisible}
        onCancel={handleCancel}
        footer={null}
        width={600}
      >
        {isAdmin && (
          <Alert
            message="Розширені права адміністратора"
            description="Як адміністратор, ви можете змінити статус звернення на будь-який інший, включаючи повернення в статус 'Новий'."
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          autoComplete="off"
        >
          <Form.Item
            label="Новий статус"
            name="new_status"
            rules={[
              {
                required: true,
                message: 'Будь ласка, оберіть новий статус',
              },
            ]}
          >
            <Select
              placeholder="Оберіть новий статус"
              size="large"
            >
              {availableStatuses.map((status) => (
                <Option key={status.value} value={status.value}>
                  {status.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="Коментар (обов'язковий)"
            name="comment"
            rules={[
              {
                required: true,
                message: 'Будь ласка, введіть коментар',
              },
              {
                min: 10,
                message: 'Коментар повинен містити мінімум 10 символів',
              },
            ]}
          >
            <TextArea
              rows={4}
              placeholder="Введіть причину зміни статусу або додаткову інформацію..."
              maxLength={500}
              showCount
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0 }}>
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button onClick={handleCancel}>
                Скасувати
              </Button>
              <Button type="primary" htmlType="submit" loading={loading}>
                Змінити статус
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};

export default ChangeStatusForm;
