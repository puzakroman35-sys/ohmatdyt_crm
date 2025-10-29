/**
 * Category Actions Components
 * Ohmatdyt CRM - Дії для категорій (активація/деактивація)
 */

import React from 'react';
import { Button, Popconfirm, message } from 'antd';
import { CheckCircleOutlined, StopOutlined } from '@ant-design/icons';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '@/store';
import {
  activateCategoryAsync,
  deactivateCategoryAsync,
  fetchCategoriesAsync,
  Category,
} from '@/store/slices/categoriesSlice';

interface CategoryActionButtonProps {
  category: Category;
  onSuccess?: () => void;
}

/**
 * Кнопка деактивації категорії
 */
export const DeactivateCategoryButton: React.FC<CategoryActionButtonProps> = ({
  category,
  onSuccess,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const [loading, setLoading] = React.useState(false);

  const handleDeactivate = async () => {
    setLoading(true);
    try {
      await dispatch(deactivateCategoryAsync(category.id)).unwrap();
      message.success('Категорію деактивовано');
      
      // Оновлюємо список
      dispatch(fetchCategoriesAsync({}));
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      message.error(error || 'Помилка при деактивації категорії');
    } finally {
      setLoading(false);
    }
  };

  if (!category.is_active) {
    return null;
  }

  return (
    <Popconfirm
      title="Деактивація категорії"
      description="Ви впевнені, що хочете деактивувати цю категорію? Вона стане недоступною для вибору при створенні нових звернень."
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
 * Кнопка активації категорії
 */
export const ActivateCategoryButton: React.FC<CategoryActionButtonProps> = ({
  category,
  onSuccess,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const [loading, setLoading] = React.useState(false);

  const handleActivate = async () => {
    setLoading(true);
    try {
      await dispatch(activateCategoryAsync(category.id)).unwrap();
      message.success('Категорію активовано');
      
      // Оновлюємо список
      dispatch(fetchCategoriesAsync({}));
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      message.error(error || 'Помилка при активації категорії');
    } finally {
      setLoading(false);
    }
  };

  if (category.is_active) {
    return null;
  }

  return (
    <Popconfirm
      title="Активація категорії"
      description="Ви впевнені, що хочете активувати цю категорію? Вона стане доступною для вибору при створенні звернень."
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
