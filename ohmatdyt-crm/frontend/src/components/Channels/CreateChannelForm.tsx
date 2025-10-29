/**
 * CreateChannelForm Component
 * Ohmatdyt CRM - Форма створення нового каналу зв'язку
 */

import React, { useEffect } from 'react';
import { Modal, Form, Input, Button, message } from 'antd';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch } from '@/store';
import {
  createChannelAsync,
  fetchChannelsAsync,
  selectChannelsLoading,
  selectChannelsError,
  clearError,
} from '@/store/slices/channelsSlice';

interface CreateChannelFormProps {
  visible: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

const CreateChannelForm: React.FC<CreateChannelFormProps> = ({
  visible,
  onClose,
  onSuccess,
}) => {
  const [form] = Form.useForm();
  const dispatch = useDispatch<AppDispatch>();
  const isLoading = useSelector(selectChannelsLoading);
  const error = useSelector(selectChannelsError);

  useEffect(() => {
    if (error) {
      message.error(error);
      dispatch(clearError());
    }
  }, [error, dispatch]);

  const handleSubmit = async (values: { name: string }) => {
    try {
      await dispatch(createChannelAsync(values)).unwrap();
      message.success('Канал успішно створено');
      form.resetFields();
      onClose();
      
      // Оновлюємо список каналів
      dispatch(fetchChannelsAsync({}));
      
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
      title="Створити новий канал зв'язку"
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
          label="Назва каналу"
          rules={[
            { required: true, message: 'Будь ласка, введіть назву каналу' },
            { min: 2, message: 'Назва має містити мінімум 2 символи' },
            { max: 100, message: 'Назва має містити максимум 100 символів' },
            {
              pattern: /^[а-яА-ЯіІїЇєЄґҐa-zA-Z0-9\s\-\/]+$/,
              message: 'Назва може містити тільки літери, цифри, пробіли, дефіси та слеші',
            },
          ]}
        >
          <Input
            placeholder="Наприклад: Телефон, Email, Viber"
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
            Створити канал
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

export default CreateChannelForm;
