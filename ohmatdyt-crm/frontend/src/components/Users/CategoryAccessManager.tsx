/**
 * Category Access Manager Component
 * Ohmatdyt CRM - FE-012
 * 
 * Компонент для управління доступами виконавців до категорій
 */

import React, { useState, useEffect } from 'react';
import { Transfer, Alert, Spin, message } from 'antd';
import type { TransferProps } from 'antd';
import { useAppDispatch } from '@/store/hooks';
import {
  fetchCategoryAccessAsync,
  updateCategoryAccessAsync,
  CategoryAccess,
} from '@/store/slices/usersSlice';
import { fetchCategoriesAsync } from '@/store/slices/categoriesSlice';
import api from '@/lib/api';

interface CategoryAccessManagerProps {
  userId: string;
  userRole: string;
  onAccessChanged?: () => void;
}

interface TransferItem {
  key: string;
  title: string;
  description?: string;
}

const CategoryAccessManager: React.FC<CategoryAccessManagerProps> = ({
  userId,
  userRole,
  onAccessChanged,
}) => {
  const dispatch = useAppDispatch();
  
  // Стан
  const [loading, setLoading] = useState(false);
  const [allCategories, setAllCategories] = useState<TransferItem[]>([]);
  const [targetKeys, setTargetKeys] = useState<string[]>([]);
  const [selectedKeys, setSelectedKeys] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [initialTargetKeys, setInitialTargetKeys] = useState<string[]>([]);

  // Завантаження даних при mount
  useEffect(() => {
    if (userRole === 'EXECUTOR') {
      loadData();
    }
  }, [userId, userRole]);

  // Завантаження категорій та доступів
  const loadData = async () => {
    setLoading(true);
    try {
      // Завантаження всіх активних категорій
      const categoriesResponse = await api.get('/api/categories', {
        params: { is_active: true, limit: 1000 },
      });
      
      const categories = categoriesResponse.data.categories || categoriesResponse.data || [];
      const categoryItems: TransferItem[] = categories.map((cat: any) => ({
        key: cat.id,
        title: cat.name,
        description: cat.description || undefined,
      }));
      
      setAllCategories(categoryItems);

      // Завантаження поточних доступів виконавця
      try {
        const accessResponse = await dispatch(fetchCategoryAccessAsync(userId)).unwrap();
        const currentAccessIds = accessResponse.categories.map((cat: CategoryAccess) => cat.category_id);
        setTargetKeys(currentAccessIds);
        setInitialTargetKeys(currentAccessIds);
        setHasChanges(false);
      } catch (error) {
        // Якщо помилка при завантаженні доступів - просто залишаємо порожній список
        console.warn('No category access found:', error);
        setTargetKeys([]);
        setInitialTargetKeys([]);
      }
    } catch (error: any) {
      console.error('Error loading data:', error);
      message.error(error.response?.data?.detail || 'Помилка завантаження даних');
    } finally {
      setLoading(false);
    }
  };

  // Обробка зміни вибраних категорій
  const handleChange: TransferProps<any>['onChange'] = (newTargetKeys) => {
    const keys = newTargetKeys.map(String);
    setTargetKeys(keys);
    
    // Перевірка чи є зміни відносно початкового стану
    const hasModifications = 
      keys.length !== initialTargetKeys.length ||
      !keys.every((key) => initialTargetKeys.includes(key));
    
    setHasChanges(hasModifications);
  };

  // Обробка вибору елементів
  const handleSelectChange: TransferProps['onSelectChange'] = (sourceSelectedKeys, targetSelectedKeys) => {
    const allKeys = [...sourceSelectedKeys, ...targetSelectedKeys].map(String);
    setSelectedKeys(allKeys);
  };

  // Збереження змін
  const handleSave = async () => {
    setSaving(true);
    try {
      await dispatch(updateCategoryAccessAsync({
        userId,
        categoryIds: targetKeys,
      })).unwrap();
      
      message.success('Доступи до категорій успішно оновлено');
      setInitialTargetKeys(targetKeys);
      setHasChanges(false);
      
      if (onAccessChanged) {
        onAccessChanged();
      }
    } catch (error: any) {
      console.error('Error saving category access:', error);
      message.error(error || 'Помилка збереження доступів');
    } finally {
      setSaving(false);
    }
  };

  // Скидання змін
  const handleReset = () => {
    setTargetKeys(initialTargetKeys);
    setHasChanges(false);
    message.info('Зміни скасовано');
  };

  // Якщо не EXECUTOR - не показуємо компонент
  if (userRole !== 'EXECUTOR') {
    return null;
  }

  return (
    <div style={{ marginTop: 24 }}>
      <h3>Доступ до категорій</h3>
      
      {targetKeys.length === 0 && !hasChanges && (
        <Alert
          message="Увага!"
          description="Виконавець не має доступу до жодної категорії. Без доступів виконавець не зможе бачити та обробляти звернення."
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {loading ? (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin tip="Завантаження категорій..." />
        </div>
      ) : (
        <>
          <Transfer
            dataSource={allCategories}
            titles={['Доступні категорії', 'Обрані категорії']}
            targetKeys={targetKeys}
            selectedKeys={selectedKeys}
            onChange={handleChange}
            onSelectChange={handleSelectChange}
            render={(item) => item.title}
            showSearch
            filterOption={(inputValue, item) =>
              item.title.toLowerCase().indexOf(inputValue.toLowerCase()) !== -1
            }
            listStyle={{
              width: 300,
              height: 400,
            }}
            locale={{
              itemUnit: 'категорія',
              itemsUnit: 'категорії',
              searchPlaceholder: 'Пошук категорій',
              notFoundContent: 'Категорії не знайдено',
            }}
          />

          {hasChanges && (
            <Alert
              message="Є незбережені зміни"
              description={
                <div>
                  <p>Натисніть "Зберегти доступи" щоб застосувати зміни або "Скасувати" для відміни.</p>
                  <div style={{ marginTop: 8 }}>
                    <button
                      onClick={handleSave}
                      disabled={saving}
                      style={{
                        marginRight: 8,
                        padding: '4px 15px',
                        backgroundColor: '#1890ff',
                        color: 'white',
                        border: 'none',
                        borderRadius: 4,
                        cursor: saving ? 'not-allowed' : 'pointer',
                      }}
                    >
                      {saving ? 'Збереження...' : 'Зберегти доступи'}
                    </button>
                    <button
                      onClick={handleReset}
                      disabled={saving}
                      style={{
                        padding: '4px 15px',
                        backgroundColor: '#fff',
                        color: '#000',
                        border: '1px solid #d9d9d9',
                        borderRadius: 4,
                        cursor: saving ? 'not-allowed' : 'pointer',
                      }}
                    >
                      Скасувати
                    </button>
                  </div>
                </div>
              }
              type="info"
              showIcon
              style={{ marginTop: 16 }}
            />
          )}

          {!hasChanges && targetKeys.length > 0 && (
            <Alert
              message={`Виконавець має доступ до ${targetKeys.length} ${targetKeys.length === 1 ? 'категорії' : 'категорій'}`}
              type="success"
              showIcon
              style={{ marginTop: 16 }}
            />
          )}
        </>
      )}
    </div>
  );
};

export default CategoryAccessManager;
