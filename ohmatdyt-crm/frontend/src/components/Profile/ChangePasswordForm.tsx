/**
 * ChangePasswordForm Component
 * FE-014: Форма зміни пароля користувача
 * Ohmatdyt CRM
 */

import React, { useState } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Typography,
  Space,
  Alert,
  Progress,
  message,
} from 'antd';
import { LockOutlined, EyeInvisibleOutlined, EyeTwoTone } from '@ant-design/icons';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { changePasswordAsync } from '@/store/slices/authSlice';

const { Title, Text } = Typography;

interface PasswordFormValues {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

interface ChangePasswordFormProps {
  onSuccess?: () => void;
}

const ChangePasswordForm: React.FC<ChangePasswordFormProps> = ({ onSuccess }) => {
  const [form] = Form.useForm();
  const dispatch = useAppDispatch();
  const { isLoading, error } = useAppSelector((state) => state.auth);
  const [passwordStrength, setPasswordStrength] = useState(0);
  const [passwordStrengthText, setPasswordStrengthText] = useState('');
  const [passwordStrengthColor, setPasswordStrengthColor] = useState<'#ff4d4f' | '#faad14' | '#52c41a'>('#ff4d4f');

  /**
   * Обчислення сили пароля
   */
  const calculatePasswordStrength = (password: string): number => {
    let strength = 0;

    if (!password) return 0;

    // Довжина
    if (password.length >= 8) strength += 25;
    if (password.length >= 12) strength += 10;
    if (password.length >= 16) strength += 10;

    // Велика літера
    if (/[A-Z]/.test(password)) strength += 20;

    // Маленька літера
    if (/[a-z]/.test(password)) strength += 20;

    // Цифра
    if (/\d/.test(password)) strength += 15;

    // Спеціальні символи
    if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) strength += 10;

    return Math.min(strength, 100);
  };

  /**
   * Обробка зміни нового пароля
   */
  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const password = e.target.value;
    const strength = calculatePasswordStrength(password);
    setPasswordStrength(strength);

    // Визначення кольору та тексту
    if (strength < 40) {
      setPasswordStrengthColor('#ff4d4f');
      setPasswordStrengthText('Слабкий');
    } else if (strength < 70) {
      setPasswordStrengthColor('#faad14');
      setPasswordStrengthText('Середній');
    } else {
      setPasswordStrengthColor('#52c41a');
      setPasswordStrengthText('Сильний');
    }
  };

  /**
   * Валідація пароля на клієнті
   */
  const validatePassword = (_: any, value: string) => {
    if (!value) {
      return Promise.reject(new Error('Будь ласка, введіть новий пароль'));
    }

    if (value.length < 8) {
      return Promise.reject(new Error('Пароль повинен містити мінімум 8 символів'));
    }

    if (!/[A-Z]/.test(value)) {
      return Promise.reject(new Error('Пароль повинен містити хоча б одну велику літеру'));
    }

    if (!/[a-z]/.test(value)) {
      return Promise.reject(new Error('Пароль повинен містити хоча б одну маленьку літеру'));
    }

    if (!/\d/.test(value)) {
      return Promise.reject(new Error('Пароль повинен містити хоча б одну цифру'));
    }

    return Promise.resolve();
  };

  /**
   * Валідація підтвердження пароля
   */
  const validateConfirmPassword = (_: any, value: string) => {
    const newPassword = form.getFieldValue('new_password');
    
    if (!value) {
      return Promise.reject(new Error('Будь ласка, підтвердіть новий пароль'));
    }

    if (value !== newPassword) {
      return Promise.reject(new Error('Паролі не співпадають'));
    }

    return Promise.resolve();
  };

  /**
   * Обробка submit форми
   */
  const handleSubmit = async (values: PasswordFormValues) => {
    try {
      const result = await dispatch(changePasswordAsync(values)).unwrap();
      
      // Успіх
      message.success('Пароль успішно змінено');
      form.resetFields();
      setPasswordStrength(0);
      setPasswordStrengthText('');
      
      // Викликаємо callback
      if (onSuccess) {
        onSuccess();
      }
    } catch (err: any) {
      // Помилка вже оброблена в thunk та збережена в state.error
      message.error(err || 'Не вдалося змінити пароль');
    }
  };

  return (
    <Card
      title={
        <Space>
          <LockOutlined />
          <Title level={4} style={{ margin: 0 }}>
            Зміна пароля
          </Title>
        </Space>
      }
      bordered={false}
    >
      {error && (
        <Alert
          message="Помилка"
          description={error}
          type="error"
          showIcon
          closable
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
          label="Поточний пароль"
          name="current_password"
          rules={[
            { required: true, message: 'Будь ласка, введіть поточний пароль' },
          ]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="Введіть поточний пароль"
            size="large"
            iconRender={(visible) =>
              visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />
            }
          />
        </Form.Item>

        <Form.Item
          label="Новий пароль"
          name="new_password"
          rules={[{ validator: validatePassword }]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="Введіть новий пароль"
            size="large"
            onChange={handlePasswordChange}
            iconRender={(visible) =>
              visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />
            }
          />
        </Form.Item>

        {/* Індикатор сили пароля */}
        {passwordStrength > 0 && (
          <div style={{ marginBottom: 24, marginTop: -8 }}>
            <Progress
              percent={passwordStrength}
              strokeColor={passwordStrengthColor}
              showInfo={false}
              size="small"
            />
            <Text
              type="secondary"
              style={{ fontSize: 12, color: passwordStrengthColor }}
            >
              Сила пароля: {passwordStrengthText}
            </Text>
          </div>
        )}

        <Form.Item
          label="Підтвердження нового пароля"
          name="confirm_password"
          dependencies={['new_password']}
          rules={[{ validator: validateConfirmPassword }]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="Підтвердіть новий пароль"
            size="large"
            iconRender={(visible) =>
              visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />
            }
          />
        </Form.Item>

        <Form.Item style={{ marginBottom: 0 }}>
          <Button
            type="primary"
            htmlType="submit"
            size="large"
            block
            loading={isLoading}
            icon={<LockOutlined />}
          >
            Змінити пароль
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default ChangePasswordForm;
