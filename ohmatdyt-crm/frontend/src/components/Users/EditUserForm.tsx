/**
 * Edit User Form Component
 * Ohmatdyt CRM - FE-008, FE-012
 */

import React, { useState, useEffect } from 'react';
import { Modal, Form, Input, Select, Switch, Button, message, Divider } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { useAppDispatch } from '@/store/hooks';
import { updateUserAsync, UpdateUserData, User, UserRole } from '@/store/slices/usersSlice';
import CategoryAccessManager from './CategoryAccessManager'; // FE-012

const { Option } = Select;

interface EditUserFormProps {
  visible: boolean;
  user: User | null;
  onCancel: () => void;
  onSuccess: () => void;
}

// Лейбли для ролей
const roleLabels: Record<UserRole, string> = {
  OPERATOR: 'Оператор',
  EXECUTOR: 'Виконавець',
  ADMIN: 'Адміністратор',
};

const EditUserForm: React.FC<EditUserFormProps> = ({
  visible,
  user,
  onCancel,
  onSuccess,
}) => {
  const dispatch = useAppDispatch();
  const [form] = Form.useForm();
  const [isLoading, setIsLoading] = useState(false);

  // Заповнюємо форму при зміні користувача
  useEffect(() => {
    if (user && visible) {
      form.setFieldsValue({
        username: user.username,
        email: user.email,
        full_name: user.full_name,
        role: user.role,
        is_active: user.is_active,
      });
    }
  }, [user, visible, form]);

  // Обробка відправки форми
  const handleSubmit = async () => {
    if (!user) return;

    try {
      const values = await form.validateFields();
      setIsLoading(true);

      const userData: UpdateUserData = {
        username: values.username,
        email: values.email,
        full_name: values.full_name,
        role: values.role,
        is_active: values.is_active,
      };

      // Додаємо пароль тільки якщо він вказаний
      if (values.password) {
        userData.password = values.password;
      }

      await dispatch(updateUserAsync({ 
        userId: user.id, 
        userData 
      })).unwrap();
      
      message.success('Користувача успішно оновлено');
      form.resetFields();
      onSuccess();
    } catch (error: any) {
      console.error('Update user error:', error);
      message.error(error || 'Помилка оновлення користувача');
    } finally {
      setIsLoading(false);
    }
  };

  // Обробка скасування
  const handleCancel = () => {
    form.resetFields();
    onCancel();
  };

  return (
    <Modal
      title={
        <span>
          <EditOutlined style={{ marginRight: 8 }} />
          Редагувати користувача
        </span>
      }
      open={visible}
      onCancel={handleCancel}
      footer={[
        <Button key="cancel" onClick={handleCancel}>
          Скасувати
        </Button>,
        <Button
          key="submit"
          type="primary"
          loading={isLoading}
          onClick={handleSubmit}
          icon={<EditOutlined />}
        >
          Зберегти
        </Button>,
      ]}
      width={user?.role === 'EXECUTOR' ? 900 : 600} // FE-012: більша ширина для EXECUTOR
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
      >
        <Form.Item
          name="username"
          label="Логін"
          rules={[
            { required: true, message: 'Будь ласка, введіть логін' },
            { min: 3, message: 'Логін повинен містити мінімум 3 символи' },
            { max: 50, message: 'Логін не може перевищувати 50 символів' },
            {
              pattern: /^[a-zA-Z0-9_-]+$/,
              message: 'Логін може містити лише латинські літери, цифри, _ та -',
            },
          ]}
        >
          <Input placeholder="username" autoComplete="off" />
        </Form.Item>

        <Form.Item
          name="email"
          label="Email"
          rules={[
            { required: true, message: 'Будь ласка, введіть email' },
            { type: 'email', message: 'Будь ласка, введіть коректний email' },
          ]}
        >
          <Input placeholder="user@example.com" autoComplete="off" />
        </Form.Item>

        <Form.Item
          name="full_name"
          label="ПІБ"
          rules={[
            { required: true, message: 'Будь ласка, введіть ПІБ' },
            { min: 3, message: 'ПІБ повинно містити мінімум 3 символи' },
            { max: 100, message: 'ПІБ не може перевищувати 100 символів' },
          ]}
        >
          <Input placeholder="Прізвище Ім'я По-батькові" />
        </Form.Item>

        <Form.Item
          name="password"
          label="Новий пароль (залиште пустим, якщо не міняєте)"
          rules={[
            { min: 8, message: 'Пароль повинен містити мінімум 8 символів' },
            {
              pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/,
              message: 'Пароль повинен містити великі та малі літери, цифри',
            },
          ]}
          hasFeedback
        >
          <Input.Password
            placeholder="Введіть новий пароль (опціонально)"
            autoComplete="new-password"
          />
        </Form.Item>

        <Form.Item
          name="confirm_password"
          label="Підтвердження пароля"
          dependencies={['password']}
          rules={[
            ({ getFieldValue }) => ({
              validator(_, value) {
                const password = getFieldValue('password');
                if (!password || !value || password === value) {
                  return Promise.resolve();
                }
                return Promise.reject(new Error('Паролі не співпадають'));
              },
            }),
          ]}
          hasFeedback
        >
          <Input.Password
            placeholder="Підтвердіть новий пароль"
            autoComplete="new-password"
          />
        </Form.Item>

        <Form.Item
          name="role"
          label="Роль"
          rules={[{ required: true, message: 'Будь ласка, виберіть роль' }]}
        >
          <Select placeholder="Виберіть роль">
            {Object.entries(roleLabels).map(([key, label]) => (
              <Option key={key} value={key}>
                {label}
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          name="is_active"
          label="Активний"
          valuePropName="checked"
        >
          <Switch checkedChildren="Так" unCheckedChildren="Ні" />
        </Form.Item>

        {/* FE-012: Секція управління доступами до категорій для EXECUTOR */}
        {user?.role === 'EXECUTOR' && (
          <>
            <Divider />
            <CategoryAccessManager
              userId={user.id}
              userRole={user.role}
              onAccessChanged={() => {
                // Опціонально: можна оновити інформацію про користувача
                console.log('Category access updated for user:', user.id);
              }}
            />
          </>
        )}
      </Form>
    </Modal>
  );
};

export default EditUserForm;
