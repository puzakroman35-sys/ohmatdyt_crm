/**
 * AssignExecutorForm Component
 * FE-011: Форма для призначення/зняття відповідального виконавця (ADMIN only)
 * Ohmatdyt CRM
 */

import React, { useState, useEffect } from 'react';
import { Button, Modal, Form, Select, message, Space, Spin, Alert } from 'antd';
import { UserAddOutlined, UserDeleteOutlined } from '@ant-design/icons';
import api from '@/lib/api';
import { CaseAssignmentRequest, User, CaseDetail } from '@/types/case';

const { Option } = Select;

interface AssignExecutorFormProps {
  caseDetail: CaseDetail;
  onSuccess: () => void;
}

const AssignExecutorForm: React.FC<AssignExecutorFormProps> = ({
  caseDetail,
  onSuccess,
}) => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [executors, setExecutors] = useState<User[]>([]);
  const [loadingExecutors, setLoadingExecutors] = useState(false);
  const [form] = Form.useForm();

  // Завантаження списку виконавців при відкритті модального вікна
  useEffect(() => {
    if (isModalVisible) {
      fetchExecutors();
    }
  }, [isModalVisible]);

  const fetchExecutors = async () => {
    setLoadingExecutors(true);
    try {
      // Отримуємо список користувачів з роллю EXECUTOR та ADMIN
      const response = await api.get('/api/users', {
        params: {
          is_active: true,
          limit: 100,
        },
      });

      // Фільтруємо тільки EXECUTOR та ADMIN
      const filteredExecutors = (response.data.users || []).filter(
        (user: User) => user.role === 'EXECUTOR' || user.role === 'ADMIN'
      );

      setExecutors(filteredExecutors);
    } catch (err: any) {
      console.error('Failed to load executors:', err);
      message.error('Помилка завантаження списку виконавців');
    } finally {
      setLoadingExecutors(false);
    }
  };

  const showModal = () => {
    // Заповнюємо форму поточним відповідальним (якщо є)
    form.setFieldsValue({
      assigned_to_id: caseDetail.responsible?.id || null,
    });
    setIsModalVisible(true);
  };

  const handleCancel = () => {
    setIsModalVisible(false);
    form.resetFields();
  };

  const handleSubmit = async (values: { assigned_to_id: string | null }) => {
    setLoading(true);
    try {
      const assignmentData: CaseAssignmentRequest = {
        assigned_to_id: values.assigned_to_id || null,
      };

      await api.patch(`/api/cases/${caseDetail.id}/assign`, assignmentData);

      if (assignmentData.assigned_to_id === null) {
        message.success('Відповідального виконавця знято. Звернення повернуто в статус "Новий"');
      } else {
        message.success('Відповідального виконавця успішно призначено');
      }

      setIsModalVisible(false);
      form.resetFields();
      onSuccess(); // Перезавантажити дані
    } catch (err: any) {
      console.error('Failed to assign executor:', err);
      const errorMessage = err.response?.data?.detail || 'Помилка при призначенні виконавця';
      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Кнопка "Зняти виконавця" якщо виконавець призначений
  const handleUnassign = async () => {
    Modal.confirm({
      title: 'Зняти відповідального виконавця?',
      content: 'Звернення буде повернуто в статус "Новий" та стане доступним для інших виконавців.',
      okText: 'Так, зняти',
      cancelText: 'Скасувати',
      okButtonProps: { danger: true },
      onOk: async () => {
        setLoading(true);
        try {
          const assignmentData: CaseAssignmentRequest = {
            assigned_to_id: null,
          };

          await api.patch(`/api/cases/${caseDetail.id}/assign`, assignmentData);

          message.success('Відповідального виконавця знято. Звернення повернуто в статус "Новий"');
          onSuccess(); // Перезавантажити дані
        } catch (err: any) {
          console.error('Failed to unassign executor:', err);
          const errorMessage = err.response?.data?.detail || 'Помилка при знятті виконавця';
          message.error(errorMessage);
        } finally {
          setLoading(false);
        }
      },
    });
  };

  return (
    <>
      <Space>
        <Button
          type="default"
          icon={<UserAddOutlined />}
          onClick={showModal}
          size="large"
        >
          {caseDetail.responsible ? 'Змінити виконавця' : 'Призначити виконавця'}
        </Button>

        {caseDetail.responsible && (
          <Button
            type="default"
            danger
            icon={<UserDeleteOutlined />}
            onClick={handleUnassign}
            size="large"
            loading={loading}
          >
            Зняти виконавця
          </Button>
        )}
      </Space>

      <Modal
        title={`Призначення виконавця для звернення #${caseDetail.public_id}`}
        open={isModalVisible}
        onCancel={handleCancel}
        footer={null}
        width={600}
        destroyOnClose
      >
        {loadingExecutors ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin size="large" />
            <div style={{ marginTop: 16 }}>Завантаження списку виконавців...</div>
          </div>
        ) : (
          <>
            <Alert
              message="Інформація"
              description={
                caseDetail.responsible
                  ? `Поточний відповідальний: ${caseDetail.responsible.full_name} (${caseDetail.responsible.username}). Оберіть нового виконавця або зніміть поточного.`
                  : 'Оберіть виконавця зі списку. При призначенні статус звернення зміниться на "В роботі".'
              }
              type="info"
              showIcon
              style={{ marginBottom: 24 }}
            />

            <Form
              form={form}
              layout="vertical"
              onFinish={handleSubmit}
              autoComplete="off"
            >
              <Form.Item
                label="Відповідальний виконавець"
                name="assigned_to_id"
                rules={[
                  {
                    required: true,
                    message: 'Будь ласка, оберіть виконавця або зніміть поточного',
                  },
                ]}
              >
                <Select
                  placeholder="Оберіть виконавця"
                  size="large"
                  showSearch
                  optionFilterProp="children"
                  allowClear
                  filterOption={(input, option) => {
                    const label = option?.label || '';
                    return String(label).toLowerCase().includes(input.toLowerCase());
                  }}
                >
                  {executors.map((executor) => (
                    <Option key={executor.id} value={executor.id}>
                      {executor.full_name} ({executor.username}) - {executor.role}
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              <Alert
                message="Зміна статусу"
                description={
                  <>
                    <strong>При призначенні виконавця:</strong> статус → "В роботі" (IN_PROGRESS)
                    <br />
                    <strong>При знятті виконавця:</strong> статус → "Новий" (NEW)
                  </>
                }
                type="warning"
                showIcon
                style={{ marginBottom: 24 }}
              />

              <Form.Item style={{ marginBottom: 0 }}>
                <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
                  <Button onClick={handleCancel}>
                    Скасувати
                  </Button>
                  <Button type="primary" htmlType="submit" loading={loading}>
                    Призначити виконавця
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </>
        )}
      </Modal>
    </>
  );
};

export default AssignExecutorForm;
