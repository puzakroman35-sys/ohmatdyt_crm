/**
 * EditCaseFieldsForm Component
 * FE-011: Форма для редагування полів звернення (ADMIN only)
 * Ohmatdyt CRM
 */

import React, { useState, useEffect } from 'react';
import { Button, Modal, Form, Select, Input, message, Space, Spin } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import api from '@/lib/api';
import { CaseUpdateRequest, Category, Channel, CaseDetail } from '@/types/case';

const { TextArea } = Input;
const { Option } = Select;

interface EditCaseFieldsFormProps {
  caseDetail: CaseDetail;
  onSuccess: () => void;
}

const EditCaseFieldsForm: React.FC<EditCaseFieldsFormProps> = ({
  caseDetail,
  onSuccess,
}) => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [categories, setCategories] = useState<Category[]>([]);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loadingData, setLoadingData] = useState(false);
  const [form] = Form.useForm();

  // Завантаження категорій та каналів при відкритті модального вікна
  useEffect(() => {
    if (isModalVisible) {
      fetchCategoriesAndChannels();
    }
  }, [isModalVisible]);

  const fetchCategoriesAndChannels = async () => {
    setLoadingData(true);
    try {
      const [categoriesRes, channelsRes] = await Promise.all([
        api.get('/api/categories'),
        api.get('/api/channels'),
      ]);

      setCategories(categoriesRes.data.categories || []);
      setChannels(channelsRes.data.channels || []);
    } catch (err: any) {
      console.error('Failed to load categories/channels:', err);
      message.error('Помилка завантаження категорій та каналів');
    } finally {
      setLoadingData(false);
    }
  };

  const showModal = () => {
    // Заповнюємо форму поточними значеннями
    form.setFieldsValue({
      category_id: caseDetail.category.id,
      channel_id: caseDetail.channel.id,
      subcategory: caseDetail.subcategory || '',
      applicant_name: caseDetail.applicant_name,
      applicant_phone: caseDetail.applicant_phone || '',
      applicant_email: caseDetail.applicant_email || '',
      summary: caseDetail.summary,
    });
    setIsModalVisible(true);
  };

  const handleCancel = () => {
    setIsModalVisible(false);
    form.resetFields();
  };

  const handleSubmit = async (values: CaseUpdateRequest) => {
    setLoading(true);
    try {
      // Видаляємо порожні поля
      const updateData: CaseUpdateRequest = {};
      if (values.category_id && values.category_id !== caseDetail.category.id) {
        updateData.category_id = values.category_id;
      }
      if (values.channel_id && values.channel_id !== caseDetail.channel.id) {
        updateData.channel_id = values.channel_id;
      }
      if (values.subcategory !== caseDetail.subcategory) {
        updateData.subcategory = values.subcategory || undefined;
      }
      if (values.applicant_name && values.applicant_name !== caseDetail.applicant_name) {
        updateData.applicant_name = values.applicant_name;
      }
      if (values.applicant_phone !== caseDetail.applicant_phone) {
        updateData.applicant_phone = values.applicant_phone || undefined;
      }
      if (values.applicant_email !== caseDetail.applicant_email) {
        updateData.applicant_email = values.applicant_email || undefined;
      }
      if (values.summary && values.summary !== caseDetail.summary) {
        updateData.summary = values.summary;
      }

      // Якщо немає змін
      if (Object.keys(updateData).length === 0) {
        message.info('Немає змін для збереження');
        setIsModalVisible(false);
        return;
      }

      await api.patch(`/api/cases/${caseDetail.id}`, updateData);

      message.success('Поля звернення успішно оновлено');
      setIsModalVisible(false);
      form.resetFields();
      onSuccess(); // Перезавантажити дані
    } catch (err: any) {
      console.error('Failed to update case fields:', err);
      const errorMessage = err.response?.data?.detail || 'Помилка при оновленні полів звернення';
      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Button
        type="default"
        icon={<EditOutlined />}
        onClick={showModal}
        size="large"
      >
        Редагувати звернення
      </Button>

      <Modal
        title={`Редагування звернення #${caseDetail.public_id}`}
        open={isModalVisible}
        onCancel={handleCancel}
        footer={null}
        width={800}
        destroyOnClose
      >
        {loadingData ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin size="large" />
            <div style={{ marginTop: 16 }}>Завантаження...</div>
          </div>
        ) : (
          <Form
            form={form}
            layout="vertical"
            onFinish={handleSubmit}
            autoComplete="off"
          >
            {/* Категорія */}
            <Form.Item
              label="Категорія"
              name="category_id"
              rules={[
                {
                  required: true,
                  message: 'Будь ласка, оберіть категорію',
                },
              ]}
            >
              <Select
                placeholder="Оберіть категорію"
                size="large"
                showSearch
                optionFilterProp="children"
              >
                {categories.map((cat) => (
                  <Option key={cat.id} value={cat.id}>
                    {cat.name}
                  </Option>
                ))}
              </Select>
            </Form.Item>

            {/* Підкатегорія */}
            <Form.Item
              label="Підкатегорія (необов'язково)"
              name="subcategory"
            >
              <Input
                placeholder="Введіть підкатегорію"
                size="large"
                maxLength={200}
              />
            </Form.Item>

            {/* Канал звернення */}
            <Form.Item
              label="Канал звернення"
              name="channel_id"
              rules={[
                {
                  required: true,
                  message: 'Будь ласка, оберіть канал звернення',
                },
              ]}
            >
              <Select
                placeholder="Оберіть канал"
                size="large"
                showSearch
                optionFilterProp="children"
              >
                {channels.map((ch) => (
                  <Option key={ch.id} value={ch.id}>
                    {ch.name}
                  </Option>
                ))}
              </Select>
            </Form.Item>

            {/* Ім'я заявника */}
            <Form.Item
              label="Ім'я заявника"
              name="applicant_name"
              rules={[
                {
                  required: true,
                  message: "Будь ласка, введіть ім'я заявника",
                },
                {
                  min: 1,
                  max: 200,
                  message: "Ім'я повинно містити від 1 до 200 символів",
                },
              ]}
            >
              <Input
                placeholder="Введіть ім'я заявника"
                size="large"
                maxLength={200}
              />
            </Form.Item>

            {/* Телефон */}
            <Form.Item
              label="Телефон (необов'язково)"
              name="applicant_phone"
              rules={[
                {
                  pattern: /^[\d\s\-\+\(\)]+$/,
                  message: 'Невірний формат телефону',
                },
              ]}
            >
              <Input
                placeholder="+380XXXXXXXXX"
                size="large"
                maxLength={50}
              />
            </Form.Item>

            {/* Email */}
            <Form.Item
              label="Email (необов'язково)"
              name="applicant_email"
              rules={[
                {
                  type: 'email',
                  message: 'Невірний формат email',
                },
              ]}
            >
              <Input
                placeholder="email@example.com"
                size="large"
                type="email"
              />
            </Form.Item>

            {/* Суть звернення */}
            <Form.Item
              label="Суть звернення"
              name="summary"
              rules={[
                {
                  required: true,
                  message: 'Будь ласка, введіть суть звернення',
                },
                {
                  min: 1,
                  message: 'Опис повинен містити мінімум 1 символ',
                },
              ]}
            >
              <TextArea
                rows={6}
                placeholder="Опишіть суть звернення..."
                maxLength={5000}
                showCount
              />
            </Form.Item>

            <Form.Item style={{ marginBottom: 0 }}>
              <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
                <Button onClick={handleCancel}>
                  Скасувати
                </Button>
                <Button type="primary" htmlType="submit" loading={loading}>
                  Зберегти зміни
                </Button>
              </Space>
            </Form.Item>
          </Form>
        )}
      </Modal>
    </>
  );
};

export default EditCaseFieldsForm;
