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
    // Для необов'язкових полів використовуємо undefined замість порожніх рядків
    form.setFieldsValue({
      category_id: caseDetail.category.id,
      channel_id: caseDetail.channel.id,
      subcategory: caseDetail.subcategory || undefined,
      applicant_name: caseDetail.applicant_name,
      applicant_phone: caseDetail.applicant_phone || undefined,
      applicant_email: caseDetail.applicant_email || undefined,
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
      // Нормалізуємо значення (порожні рядки -> undefined для необов'язкових полів)
      const normalizeValue = (value: any) => {
        if (value === '' || value === null) return undefined;
        return value;
      };

      const normalizedValues = {
        category_id: values.category_id,
        channel_id: values.channel_id,
        subcategory: normalizeValue(values.subcategory),
        applicant_name: values.applicant_name,
        applicant_phone: normalizeValue(values.applicant_phone),
        applicant_email: normalizeValue(values.applicant_email),
        summary: values.summary,
      };

      // Відправляємо тільки змінені поля
      const updateData: CaseUpdateRequest = {};
      
      if (normalizedValues.category_id && normalizedValues.category_id !== caseDetail.category.id) {
        updateData.category_id = normalizedValues.category_id;
      }
      
      if (normalizedValues.channel_id && normalizedValues.channel_id !== caseDetail.channel.id) {
        updateData.channel_id = normalizedValues.channel_id;
      }
      
      // Для subcategory порівнюємо нормалізовані значення
      const currentSubcategory = normalizeValue(caseDetail.subcategory);
      if (normalizedValues.subcategory !== currentSubcategory) {
        updateData.subcategory = normalizedValues.subcategory;
      }
      
      if (normalizedValues.applicant_name && normalizedValues.applicant_name !== caseDetail.applicant_name) {
        updateData.applicant_name = normalizedValues.applicant_name;
      }
      
      // Для phone порівнюємо нормалізовані значення
      const currentPhone = normalizeValue(caseDetail.applicant_phone);
      if (normalizedValues.applicant_phone !== currentPhone) {
        updateData.applicant_phone = normalizedValues.applicant_phone;
      }
      
      // Для email порівнюємо нормалізовані значення
      const currentEmail = normalizeValue(caseDetail.applicant_email);
      if (normalizedValues.applicant_email !== currentEmail) {
        updateData.applicant_email = normalizedValues.applicant_email;
      }
      
      if (normalizedValues.summary && normalizedValues.summary !== caseDetail.summary) {
        updateData.summary = normalizedValues.summary;
      }

      // Якщо немає змін
      if (Object.keys(updateData).length === 0) {
        message.info('Немає змін для збереження');
        setIsModalVisible(false);
        return;
      }

      console.log('Відправляємо оновлені дані:', updateData);
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
