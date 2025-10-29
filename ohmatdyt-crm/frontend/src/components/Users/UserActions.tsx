/**
 * User Actions Buttons Component
 * Ohmatdyt CRM - FE-008
 * Компоненти для деактивації, активації та скидання пароля
 */

import React, { useState } from 'react';
import { Button, Popconfirm, message, Modal, Typography } from 'antd';
import {
  StopOutlined,
  CheckCircleOutlined,
  KeyOutlined,
} from '@ant-design/icons';
import { useAppDispatch } from '@/store/hooks';
import {
  deactivateUserAsync,
  activateUserAsync,
  resetPasswordAsync,
  User,
} from '@/store/slices/usersSlice';

const { Paragraph, Text } = Typography;

// ===== Deactivate User Button =====
interface DeactivateUserButtonProps {
  user: User;
  onSuccess?: () => void;
}

export const DeactivateUserButton: React.FC<DeactivateUserButtonProps> = ({
  user,
  onSuccess,
}) => {
  const dispatch = useAppDispatch();
  const [isLoading, setIsLoading] = useState(false);
  const [showForceModal, setShowForceModal] = useState(false);
  const [activeCasesCount, setActiveCasesCount] = useState(0);

  const handleDeactivate = async (force: boolean = false) => {
    setIsLoading(true);
    try {
      await dispatch(
        deactivateUserAsync({ userId: user.id, force })
      ).unwrap();
      
      message.success('Користувача успішно деактивовано');
      if (onSuccess) onSuccess();
    } catch (error: any) {
      console.error('Deactivate user error:', error);
      
      // Якщо користувач має активні справи і не використовується force
      if (error.hasActiveCases && !force) {
        setActiveCasesCount(error.activeCasesCount || 0);
        setShowForceModal(true);
      } else {
        message.error(error.message || error || 'Помилка деактивації користувача');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleForceDeactivate = async () => {
    setShowForceModal(false);
    await handleDeactivate(true);
  };

  return (
    <>
      <Popconfirm
        title="Деактивувати користувача?"
        description="Користувач не зможе увійти в систему"
        onConfirm={() => handleDeactivate(false)}
        okText="Так"
        cancelText="Ні"
        disabled={!user.is_active}
      >
        <Button
          danger
          size="small"
          icon={<StopOutlined />}
          loading={isLoading}
          disabled={!user.is_active}
        >
          Деактивувати
        </Button>
      </Popconfirm>

      {/* Modal для підтвердження деактивації з активними справами */}
      <Modal
        title="Увага! Користувач має активні справи"
        open={showForceModal}
        onOk={handleForceDeactivate}
        onCancel={() => setShowForceModal(false)}
        okText="Деактивувати примусово"
        cancelText="Скасувати"
        okButtonProps={{ danger: true }}
      >
        <Paragraph>
          Користувач <Text strong>{user.full_name}</Text> має{' '}
          <Text strong type="danger">{activeCasesCount}</Text> активних справ.
        </Paragraph>
        <Paragraph>
          Деактивація призведе до того, що ці справи залишаться без виконавця.
          Бажаєте продовжити?
        </Paragraph>
      </Modal>
    </>
  );
};

// ===== Activate User Button =====
interface ActivateUserButtonProps {
  user: User;
  onSuccess?: () => void;
}

export const ActivateUserButton: React.FC<ActivateUserButtonProps> = ({
  user,
  onSuccess,
}) => {
  const dispatch = useAppDispatch();
  const [isLoading, setIsLoading] = useState(false);

  const handleActivate = async () => {
    setIsLoading(true);
    try {
      await dispatch(activateUserAsync(user.id)).unwrap();
      
      message.success('Користувача успішно активовано');
      if (onSuccess) onSuccess();
    } catch (error: any) {
      console.error('Activate user error:', error);
      message.error(error || 'Помилка активації користувача');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Popconfirm
      title="Активувати користувача?"
      description="Користувач зможе увійти в систему"
      onConfirm={handleActivate}
      okText="Так"
      cancelText="Ні"
      disabled={user.is_active}
    >
      <Button
        type="primary"
        size="small"
        icon={<CheckCircleOutlined />}
        loading={isLoading}
        disabled={user.is_active}
      >
        Активувати
      </Button>
    </Popconfirm>
  );
};

// ===== Reset Password Button =====
interface ResetPasswordButtonProps {
  user: User;
  onSuccess?: () => void;
}

export const ResetPasswordButton: React.FC<ResetPasswordButtonProps> = ({
  user,
  onSuccess,
}) => {
  const dispatch = useAppDispatch();
  const [isLoading, setIsLoading] = useState(false);

  const handleResetPassword = async () => {
    setIsLoading(true);
    try {
      const result = await dispatch(resetPasswordAsync(user.id)).unwrap();
      
      // Показуємо модальне вікно з тимчасовим паролем
      Modal.success({
        title: 'Пароль успішно скинуто',
        content: (
          <div>
            <Paragraph>
              Тимчасовий пароль для користувача <Text strong>{user.full_name}</Text>:
            </Paragraph>
            <Paragraph
              copyable
              style={{
                backgroundColor: '#fff7e6',
                padding: '12px',
                borderRadius: '4px',
                fontSize: '16px',
                fontWeight: 'bold',
                textAlign: 'center',
                fontFamily: 'monospace',
              }}
            >
              {result.temp_password}
            </Paragraph>
            <Paragraph type="secondary" style={{ marginTop: 12 }}>
              Збережіть цей пароль і передайте користувачу. Після входу в систему
              користувач зможе змінити пароль.
            </Paragraph>
          </div>
        ),
        width: 500,
      });

      if (onSuccess) onSuccess();
    } catch (error: any) {
      console.error('Reset password error:', error);
      message.error(error || 'Помилка скидання пароля');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Popconfirm
      title="Скинути пароль?"
      description="Буде згенеровано новий тимчасовий пароль"
      onConfirm={handleResetPassword}
      okText="Так"
      cancelText="Ні"
    >
      <Button
        size="small"
        icon={<KeyOutlined />}
        loading={isLoading}
      >
        Скинути пароль
      </Button>
    </Popconfirm>
  );
};
