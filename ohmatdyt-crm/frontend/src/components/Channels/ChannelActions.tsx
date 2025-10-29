/**
 * Channel Actions Components
 * Ohmatdyt CRM - Дії для каналів (активація/деактивація)
 */

import React from 'react';
import { Button, Popconfirm, message } from 'antd';
import { CheckCircleOutlined, StopOutlined } from '@ant-design/icons';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '@/store';
import {
  activateChannelAsync,
  deactivateChannelAsync,
  fetchChannelsAsync,
  Channel,
} from '@/store/slices/channelsSlice';

interface ChannelActionButtonProps {
  channel: Channel;
  onSuccess?: () => void;
}

/**
 * Кнопка деактивації каналу
 */
export const DeactivateChannelButton: React.FC<ChannelActionButtonProps> = ({
  channel,
  onSuccess,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const [loading, setLoading] = React.useState(false);

  const handleDeactivate = async () => {
    setLoading(true);
    try {
      await dispatch(deactivateChannelAsync(channel.id)).unwrap();
      message.success('Канал деактивовано');
      
      // Оновлюємо список
      dispatch(fetchChannelsAsync({}));
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      message.error(error || 'Помилка при деактивації каналу');
    } finally {
      setLoading(false);
    }
  };

  if (!channel.is_active) {
    return null;
  }

  return (
    <Popconfirm
      title="Деактивація каналу"
      description="Ви впевнені, що хочете деактивувати цей канал? Він стане недоступним для вибору при створенні нових звернень."
      onConfirm={handleDeactivate}
      okText="Так, деактивувати"
      cancelText="Скасувати"
      okButtonProps={{ danger: true }}
    >
      <Button
        size="small"
        danger
        icon={<StopOutlined />}
        loading={loading}
      >
        Деактивувати
      </Button>
    </Popconfirm>
  );
};

/**
 * Кнопка активації каналу
 */
export const ActivateChannelButton: React.FC<ChannelActionButtonProps> = ({
  channel,
  onSuccess,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const [loading, setLoading] = React.useState(false);

  const handleActivate = async () => {
    setLoading(true);
    try {
      await dispatch(activateChannelAsync(channel.id)).unwrap();
      message.success('Канал активовано');
      
      // Оновлюємо список
      dispatch(fetchChannelsAsync({}));
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      message.error(error || 'Помилка при активації каналу');
    } finally {
      setLoading(false);
    }
  };

  if (channel.is_active) {
    return null;
  }

  return (
    <Popconfirm
      title="Активація каналу"
      description="Ви впевнені, що хочете активувати цей канал? Він стане доступним для вибору при створенні звернень."
      onConfirm={handleActivate}
      okText="Так, активувати"
      cancelText="Скасувати"
    >
      <Button
        size="small"
        type="primary"
        icon={<CheckCircleOutlined />}
        loading={loading}
      >
        Активувати
      </Button>
    </Popconfirm>
  );
};
