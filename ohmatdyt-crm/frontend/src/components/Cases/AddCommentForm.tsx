/**
 * AddCommentForm Component
 * Форма для додавання коментарів до звернення (публічних та внутрішніх)
 * Ohmatdyt CRM - FE-010
 */

import React, { useState } from 'react';
import { Form, Input, Button, Switch, Space, message, Card } from 'antd';
import { CommentOutlined, LockOutlined, UnlockOutlined } from '@ant-design/icons';
import api from '@/lib/api';

const { TextArea } = Input;

interface AddCommentFormProps {
  caseId: string;
  casePublicId: number;
  userRole?: 'OPERATOR' | 'EXECUTOR' | 'ADMIN';
  onSuccess?: () => void;
}

/**
 * Компонент форми додавання коментаря
 * 
 * RBAC Rules:
 * - Публічні коментарі (is_internal=false): Всі авторизовані користувачі
 * - Внутрішні коментарі (is_internal=true): Тільки EXECUTOR та ADMIN
 * 
 * Валідація:
 * - Мінімум 5 символів
 * - Максимум 5000 символів
 */
const AddCommentForm: React.FC<AddCommentFormProps> = ({
  caseId,
  casePublicId,
  userRole,
  onSuccess,
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [isInternal, setIsInternal] = useState(false);

  // Перевірка, чи може користувач створювати внутрішні коментарі
  const canCreateInternalComments = userRole === 'EXECUTOR' || userRole === 'ADMIN';

  const handleSubmit = async (values: { text: string }) => {
    setLoading(true);
    try {
      // POST /api/cases/{case_id}/comments
      await api.post(`/api/cases/${caseId}/comments`, {
        text: values.text.trim(),
        is_internal: isInternal,
      });

      message.success(
        isInternal 
          ? 'Внутрішній коментар успішно додано' 
          : 'Коментар успішно додано'
      );

      // Очищаємо форму
      form.resetFields();
      setIsInternal(false);

      // Викликаємо callback для оновлення списку коментарів
      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      console.error('Failed to add comment:', error);
      
      // Обробка специфічних помилок
      if (error.response?.status === 403) {
        message.error('У вас немає прав для створення внутрішніх коментарів');
      } else if (error.response?.status === 400) {
        message.error(error.response?.data?.detail || 'Помилка валідації коментаря');
      } else {
        message.error('Не вдалося додати коментар. Спробуйте ще раз.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card 
      title={
        <Space>
          <CommentOutlined />
          Додати коментар
        </Space>
      }
      bordered={false}
      style={{ marginBottom: 24 }}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
      >
        {/* Текст коментаря */}
        <Form.Item
          name="text"
          label="Текст коментаря"
          rules={[
            {
              required: true,
              message: 'Будь ласка, введіть текст коментаря',
            },
            {
              min: 5,
              message: 'Коментар повинен містити мінімум 5 символів',
            },
            {
              max: 5000,
              message: 'Коментар не може перевищувати 5000 символів',
            },
          ]}
        >
          <TextArea
            rows={4}
            placeholder="Введіть ваш коментар..."
            maxLength={5000}
            showCount
          />
        </Form.Item>

        {/* Перемикач типу коментаря (тільки для EXECUTOR/ADMIN) */}
        {canCreateInternalComments && (
          <Form.Item
            label={
              <Space>
                {isInternal ? <LockOutlined /> : <UnlockOutlined />}
                Тип коментаря
              </Space>
            }
          >
            <Space>
              <Switch
                checked={isInternal}
                onChange={setIsInternal}
                checkedChildren="Внутрішній"
                unCheckedChildren="Публічний"
              />
              <span style={{ color: isInternal ? '#fa8c16' : '#52c41a' }}>
                {isInternal 
                  ? 'Видимий тільки співробітникам системи' 
                  : 'Видимий всім учасникам звернення'}
              </span>
            </Space>
          </Form.Item>
        )}

        {/* Кнопка відправки */}
        <Form.Item style={{ marginBottom: 0 }}>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            icon={<CommentOutlined />}
            size="large"
            block
          >
            Додати коментар
          </Button>
        </Form.Item>
      </Form>

      {/* Підказка для операторів */}
      {!canCreateInternalComments && (
        <div style={{ marginTop: 16, padding: 12, background: '#f0f0f0', borderRadius: 4 }}>
          <small style={{ color: '#595959' }}>
            ℹ️ Ви можете додавати тільки публічні коментарі. 
            Внутрішні коментарі доступні для виконавців та адміністраторів.
          </small>
        </div>
      )}
    </Card>
  );
};

export default AddCommentForm;
