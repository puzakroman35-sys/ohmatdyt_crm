/**
 * EditCategoryForm Component
 * Ohmatdyt CRM - Форма редагування категорії
 */

import React, { useEffect } from 'react';
import { Modal, Form, Input, Button, message } from 'antd';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch } from '@/store';
import {
  updateCategoryAsync,
  fetchCategoriesAsync,
  selectCategoriesLoading,
  selectCategoriesError,
  clearError,
  Category,
} from '@/store/slices/categoriesSlice';

interface EditCategoryFormProps {
  visible: boolean;
  category: Category | null;
  onClose: () => void;
  onSuccess?: () => void;
}

const EditCategoryForm: React.FC<EditCategoryFormProps> = ({
  visible,
  category,
  onClose,
  onSuccess,
}) => {
  const [form] = Form.useForm();
  const dispatch = useDispatch<AppDispatch>();
  const isLoading = useSelector(selectCategoriesLoading);
  const error = useSelector(selectCategoriesError);

  useEffect(() => {
    if (category && visible) {
      form.setFieldsValue({
        name: category.name,
      });
    }
  }, [category, visible, form]);

  useEffect(() => {
    if (error) {
      message.error(error);
      dispatch(clearError());
    }
  }, [error, dispatch]);

  const handleSubmit = async (values: { name: string }) => {
    if (!category) return;

    try {
      await dispatch(
        updateCategoryAsync({
          id: category.id,
          data: values,
        })
      ).unwrap();
      
      message.success('Категорію успішно оновлено');
      form.resetFields();
      onClose();
      
      // Оновлюємо список категорій
      dispatch(fetchCategoriesAsync({}));
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (err: any) {
      // Помилка вже оброблена в slice і показана через useEffect
    }
  };

  const handleCancel = () => {
    form.resetFields();
    dispatch(clearError());
    onClose();
  };

  return (
    <Modal
      title="Редагувати категорію"
      open={visible}
      onCancel={handleCancel}
      footer={null}
      width={500}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        autoComplete="off"
      >
        <Form.Item
          name="name"
          label="Назва категорії"
          rules={[
            { required: true, message: 'Будь ласка, введіть назву категорії' },
            { min: 2, message: 'Назва має містити мінімум 2 символи' },
            { max: 100, message: 'Назва має містити максимум 100 символів' },
            {
              pattern: /^[а-яА-ЯіІїЇєЄґҐa-zA-Z0-9\s\-\/]+$/,
              message: 'Назва може містити тільки літери, цифри, пробіли, дефіси та слеші',
            },
          ]}
        >
          <Input
            placeholder="Наприклад: Медичні консультації"
            maxLength={100}
          />
        </Form.Item>

        <Form.Item style={{ marginBottom: 0, marginTop: 24 }}>
          <Button
            type="primary"
            htmlType="submit"
            loading={isLoading}
            block
            size="large"
          >
            Зберегти зміни
          </Button>
          <Button
            onClick={handleCancel}
            block
            size="large"
            style={{ marginTop: 8 }}
          >
            Скасувати
          </Button>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default EditCategoryForm;
