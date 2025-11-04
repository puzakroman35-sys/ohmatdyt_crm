/**
 * Create User Form Component
 * Ohmatdyt CRM - FE-008, FE-012
 */

import React, { useState } from 'react';
import { Modal, Form, Input, Select, Switch, Button, message, Divider } from 'antd';
import { UserAddOutlined } from '@ant-design/icons';
import { useAppDispatch } from '@/store/hooks';
import { createUserAsync, CreateUserData, UserRole } from '@/store/slices/usersSlice';
import CategorySelector from './CategorySelector'; // FE-012

const { Option } = Select;

interface CreateUserFormProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess: () => void;
}

// Лейбли для ролей
const roleLabels: Record<UserRole, string> = {
  OPERATOR: 'Оператор',
  EXECUTOR: 'Виконавець',
  ADMIN: 'Адміністратор',
};

const CreateUserForm: React.FC<CreateUserFormProps> = ({
  visible,
  onCancel,
  onSuccess,
}) => {
  const dispatch = useAppDispatch();
  const [form] = Form.useForm();
  const [isLoading, setIsLoading] = useState(false);
  const [selectedRole, setSelectedRole] = useState<UserRole>('OPERATOR'); // FE-012: відстежуємо роль
  const [selectedCategoryIds, setSelectedCategoryIds] = useState<string[]>([]); // FE-012: категорії для EXECUTOR

  // Обробка відправки форми
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setIsLoading(true);

      const userData: CreateUserData = {
        username: values.username,
        email: values.email,
        full_name: values.full_name,
        password: values.password,
        role: values.role,
        is_active: values.is_active !== undefined ? values.is_active : true,
      };

      // FE-012: Додаємо категорії для EXECUTOR
      if (values.role === 'EXECUTOR' && selectedCategoryIds.length > 0) {
        userData.executor_category_ids = selectedCategoryIds;
      }

      await dispatch(createUserAsync(userData)).unwrap();
      
      message.success('Користувача успішно створено');
      form.resetFields();
      setSelectedCategoryIds([]); // FE-012: очищаємо категорії
      setSelectedRole('OPERATOR'); // FE-012: скидаємо роль
      onSuccess();
    } catch (error: any) {
      console.error('Create user error:', error);
      message.error(error || 'Помилка створення користувача');
    } finally {
      setIsLoading(false);
    }
  };

  // Обробка скасування
  const handleCancel = () => {
    form.resetFields();
    setSelectedCategoryIds([]); // FE-012: очищаємо категорії
    setSelectedRole('OPERATOR'); // FE-012: скидаємо роль
    onCancel();
  };

  // FE-012: Обробка зміни ролі
  const handleRoleChange = (role: UserRole) => {
    setSelectedRole(role);
    // Очищаємо категорії при зміні ролі на не-EXECUTOR
    if (role !== 'EXECUTOR') {
      setSelectedCategoryIds([]);
    }
  };

  return (
    <Modal
      title={
        <span>
          <UserAddOutlined style={{ marginRight: 8 }} />
          Створити користувача
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
          icon={<UserAddOutlined />}
        >
          Створити
        </Button>,
      ]}
      width={selectedRole === 'EXECUTOR' ? 900 : 600} // FE-012: більша ширина для EXECUTOR
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          is_active: true,
          role: 'OPERATOR',
        }}
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
          label="Пароль"
          rules={[
            { required: true, message: 'Будь ласка, введіть пароль' },
            { min: 8, message: 'Пароль повинен містити мінімум 8 символів' },
            {
              pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/,
              message: 'Пароль повинен містити великі та малі літери, цифри',
            },
          ]}
          hasFeedback
        >
          <Input.Password
            placeholder="Введіть надійний пароль"
            autoComplete="new-password"
          />
        </Form.Item>

        <Form.Item
          name="confirm_password"
          label="Підтвердження пароля"
          dependencies={['password']}
          rules={[
            { required: true, message: 'Будь ласка, підтвердіть пароль' },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue('password') === value) {
                  return Promise.resolve();
                }
                return Promise.reject(new Error('Паролі не співпадають'));
              },
            }),
          ]}
          hasFeedback
        >
          <Input.Password
            placeholder="Підтвердіть пароль"
            autoComplete="new-password"
          />
        </Form.Item>

        <Form.Item
          name="role"
          label="Роль"
          rules={[{ required: true, message: 'Будь ласка, виберіть роль' }]}
        >
          <Select placeholder="Виберіть роль" onChange={handleRoleChange}>
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

        {/* FE-012: Секція вибору категорій для EXECUTOR */}
        {selectedRole === 'EXECUTOR' && (
          <>
            <Divider />
            <div>
              <h4>Доступ до категорій</h4>
              <CategorySelector
                selectedCategoryIds={selectedCategoryIds}
                onChange={setSelectedCategoryIds}
                disabled={isLoading}
              />
            </div>
          </>
        )}
      </Form>
    </Modal>
  );
};

export default CreateUserForm;
