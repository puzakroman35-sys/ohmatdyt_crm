/**
 * EditChannelForm Component
 * Ohmatdyt CRM - Форма редагування каналу зв'язку
 */

import React, { useEffect } from 'react';
import { Modal, Form, Input, Button, message } from 'antd';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch } from '@/store';
import {
  updateChannelAsync,
  fetchChannelsAsync,
  selectChannelsLoading,
  selectChannelsError,
  clearError,
  Channel,
} from '@/store/slices/channelsSlice';

interface EditChannelFormProps {
  visible: boolean;
  channel: Channel | null;
  onClose: () => void;
  onSuccess?: () => void;
}

const EditChannelForm: React.FC<EditChannelFormProps> = ({
  visible,
  channel,
  onClose,
  onSuccess,
}) => {
  const [form] = Form.useForm();
  const dispatch = useDispatch<AppDispatch>();
  const isLoading = useSelector(selectChannelsLoading);
  const error = useSelector(selectChannelsError);

  useEffect(() => {
    if (channel && visible) {
      form.setFieldsValue({
        name: channel.name,
      });
    }
  }, [channel, visible, form]);

  useEffect(() => {
    if (error) {
      message.error(error);
      dispatch(clearError());
    }
  }, [error, dispatch]);

  const handleSubmit = async (values: { name: string }) => {
    if (!channel) return;

    try {
      await dispatch(
        updateChannelAsync({
          id: channel.id,
          data: values,
        })
      ).unwrap();
      
      message.success('Канал успішно оновлено');
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
      title="Редагувати канал зв'язку"
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

export default EditChannelForm;
