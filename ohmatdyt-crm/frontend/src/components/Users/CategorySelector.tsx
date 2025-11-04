/**
 * Category Selector Component
 * Ohmatdyt CRM - FE-012
 * 
 * Компонент для вибору категорій при створенні користувача EXECUTOR
 */

import React, { useState, useEffect } from 'react';
import { Transfer, Alert, Spin, message } from 'antd';
import type { TransferProps } from 'antd';
import api from '@/lib/api';

interface CategorySelectorProps {
  selectedCategoryIds: string[];
  onChange: (categoryIds: string[]) => void;
  disabled?: boolean;
}

interface TransferItem {
  key: string;
  title: string;
  description?: string;
}

const CategorySelector: React.FC<CategorySelectorProps> = ({
  selectedCategoryIds,
  onChange,
  disabled = false,
}) => {
  const [loading, setLoading] = useState(false);
  const [allCategories, setAllCategories] = useState<TransferItem[]>([]);
  const [selectedKeys, setSelectedKeys] = useState<string[]>([]);

  // Завантаження категорій при mount
  useEffect(() => {
    loadCategories();
  }, []);

  // Завантаження всіх активних категорій
  const loadCategories = async () => {
    setLoading(true);
    try {
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
    } catch (error: any) {
      console.error('Error loading categories:', error);
      message.error(error.response?.data?.detail || 'Помилка завантаження категорій');
    } finally {
      setLoading(false);
    }
  };

  // Обробка зміни вибраних категорій
  const handleChange: TransferProps['onChange'] = (newTargetKeys) => {
    const keys = newTargetKeys.map(String);
    onChange(keys);
  };

  // Обробка вибору елементів
  const handleSelectChange: TransferProps['onSelectChange'] = (sourceSelectedKeys, targetSelectedKeys) => {
    const allKeys = [...sourceSelectedKeys, ...targetSelectedKeys].map(String);
    setSelectedKeys(allKeys);
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 40 }}>
        <Spin tip="Завантаження категорій..." />
      </div>
    );
  }

  return (
    <div style={{ marginTop: 16 }}>
      {selectedCategoryIds.length === 0 && (
        <Alert
          message="Увага!"
          description="Виконавець не має доступу до жодної категорії. Без доступів виконавець не зможе бачити та обробляти звернення."
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <Transfer
        dataSource={allCategories}
        titles={['Доступні категорії', 'Обрані категорії']}
        targetKeys={selectedCategoryIds}
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
        disabled={disabled}
      />

      {selectedCategoryIds.length > 0 && (
        <Alert
          message={`Обрано ${selectedCategoryIds.length} ${selectedCategoryIds.length === 1 ? 'категорію' : 'категорій'}`}
          type="info"
          showIcon
          style={{ marginTop: 16 }}
        />
      )}
    </div>
  );
};

export default CategorySelector;
