/**
 * Create Case Form Component
 * Форма створення звернення з завантаженням файлів
 * Ohmatdyt CRM - FE-003
 */

import React, { useState, useEffect } from 'react';
import {
  Form,
  Input,
  Select,
  Button,
  Upload,
  message,
  Space,
  Typography,
  Alert,
  Row,
  Col,
} from 'antd';
import {
  UploadOutlined,
  DeleteOutlined,
  FileOutlined,
} from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd/es/upload/interface';
import api from '@/lib/api';

const { TextArea } = Input;
const { Option } = Select;
const { Title } = Typography;

// Допустимі типи файлів
const ALLOWED_FILE_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'image/jpeg',
  'image/jpg',
  'image/png',
];

// Допустимі розширення файлів
const ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png'];

// Максимальний розмір файлу (10MB)
const MAX_FILE_SIZE = 10 * 1024 * 1024;

interface Category {
  id: string;
  name: string;
  is_active: boolean;
}

interface Channel {
  id: string;
  name: string;
  is_active: boolean;
}

interface CreateCaseFormData {
  category_id: string;
  channel_id: string;
  subcategory?: string;
  applicant_name: string;
  applicant_phone?: string;
  applicant_email?: string;
  summary: string;
}

interface CreateCaseFormProps {
  onSuccess?: (caseData: any) => void;
  onCancel?: () => void;
}

const CreateCaseForm: React.FC<CreateCaseFormProps> = ({ onSuccess, onCancel }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [categories, setCategories] = useState<Category[]>([]);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [loadingData, setLoadingData] = useState(true);

  // Завантаження категорій та каналів
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoadingData(true);
        const [categoriesRes, channelsRes] = await Promise.all([
          api.get('/api/categories'),
          api.get('/api/channels'),
        ]);

        setCategories(categoriesRes.data.filter((c: Category) => c.is_active));
        setChannels(channelsRes.data.filter((c: Channel) => c.is_active));
      } catch (error: any) {
        message.error('Помилка завантаження довідників: ' + (error.message || 'Невідома помилка'));
      } finally {
        setLoadingData(false);
      }
    };

    loadData();
  }, []);

  // Валідація файлу перед додаванням
  const beforeUpload = (file: File): boolean => {
    // Перевірка типу файлу
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    const isAllowedType = ALLOWED_FILE_TYPES.includes(file.type) || 
                          ALLOWED_EXTENSIONS.includes(fileExtension || '');
    
    if (!isAllowedType) {
      message.error(
        `Файл ${file.name} має недопустимий тип. Дозволені типи: PDF, DOC, DOCX, XLS, XLSX, JPG, PNG`
      );
      return false;
    }

    // Перевірка розміру файлу
    const isAllowedSize = file.size <= MAX_FILE_SIZE;
    if (!isAllowedSize) {
      message.error(
        `Файл ${file.name} перевищує максимальний розмір 10MB (${(file.size / 1024 / 1024).toFixed(2)}MB)`
      );
      return false;
    }

    return false; // Повертаємо false, щоб Upload не намагався завантажити файл самостійно
  };

  // Обробка зміни списку файлів
  const handleChange: UploadProps['onChange'] = ({ fileList: newFileList }) => {
    setFileList(newFileList);
  };

  // Відправка форми
  const handleSubmit = async (values: CreateCaseFormData) => {
    try {
      setLoading(true);

      // Створюємо FormData для multipart/form-data
      const formData = new FormData();
      
      // Додаємо обов'язкові поля
      formData.append('category_id', values.category_id);
      formData.append('channel_id', values.channel_id);
      formData.append('applicant_name', values.applicant_name);
      formData.append('summary', values.summary);

      // Додаємо опціональні поля
      if (values.subcategory) {
        formData.append('subcategory', values.subcategory);
      }
      if (values.applicant_phone) {
        formData.append('applicant_phone', values.applicant_phone);
      }
      if (values.applicant_email) {
        formData.append('applicant_email', values.applicant_email);
      }

      // Додаємо файли
      fileList.forEach((file) => {
        if (file.originFileObj) {
          formData.append('files', file.originFileObj);
        }
      });

      // Відправляємо запит
      const response = await api.post('/api/cases', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      message.success(
        `Звернення успішно створено! Публічний ID: #${response.data.public_id}`
      );

      // Очищуємо форму
      form.resetFields();
      setFileList([]);

      // Викликаємо callback успіху
      if (onSuccess) {
        onSuccess(response.data);
      }
    } catch (error: any) {
      console.error('Error creating case:', error);
      
      let errorMessage = 'Помилка створення звернення';
      
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        } else if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail.map((e: any) => e.msg).join(', ');
        }
      }
      
      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Видалення файлу зі списку
  const handleRemoveFile = (file: UploadFile) => {
    setFileList(fileList.filter(f => f.uid !== file.uid));
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <Title level={3} style={{ marginBottom: 24 }}>
        Створення звернення
      </Title>

      <Alert
        message="Заповніть всі обов'язкові поля та додайте необхідні файли"
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        disabled={loading || loadingData}
      >
        <Row gutter={16}>
          {/* Категорія */}
          <Col xs={24} sm={12}>
            <Form.Item
              name="category_id"
              label="Категорія"
              rules={[{ required: true, message: 'Оберіть категорію' }]}
            >
              <Select
                placeholder="Оберіть категорію"
                loading={loadingData}
                showSearch
                optionFilterProp="children"
              >
                {categories.map((category) => (
                  <Option key={category.id} value={category.id}>
                    {category.name}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Col>

          {/* Канал */}
          <Col xs={24} sm={12}>
            <Form.Item
              name="channel_id"
              label="Канал звернення"
              rules={[{ required: true, message: 'Оберіть канал' }]}
            >
              <Select
                placeholder="Оберіть канал"
                loading={loadingData}
                showSearch
                optionFilterProp="children"
              >
                {channels.map((channel) => (
                  <Option key={channel.id} value={channel.id}>
                    {channel.name}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
        </Row>

        {/* Підкатегорія (опціонально) */}
        <Form.Item
          name="subcategory"
          label="Підкатегорія (опціонально)"
        >
          <Input placeholder="Введіть підкатегорію" />
        </Form.Item>

        {/* Ім'я заявника */}
        <Form.Item
          name="applicant_name"
          label="Ім'я заявника"
          rules={[
            { required: true, message: 'Введіть ім\'я заявника' },
            { min: 2, message: 'Ім\'я має містити мінімум 2 символи' },
          ]}
        >
          <Input placeholder="Прізвище Ім'я По батькові" />
        </Form.Item>

        <Row gutter={16}>
          {/* Телефон */}
          <Col xs={24} sm={12}>
            <Form.Item
              name="applicant_phone"
              label="Телефон (опціонально)"
              rules={[
                {
                  pattern: /^[\d\s\+\-\(\)]{9,}$/,
                  message: 'Введіть коректний номер телефону (мінімум 9 цифр)',
                },
              ]}
            >
              <Input placeholder="+380XXXXXXXXX" />
            </Form.Item>
          </Col>

          {/* Email */}
          <Col xs={24} sm={12}>
            <Form.Item
              name="applicant_email"
              label="Email (опціонально)"
              rules={[
                {
                  type: 'email',
                  message: 'Введіть коректну email адресу',
                },
              ]}
            >
              <Input placeholder="email@example.com" />
            </Form.Item>
          </Col>
        </Row>

        {/* Суть звернення */}
        <Form.Item
          name="summary"
          label="Суть звернення"
          rules={[
            { required: true, message: 'Опишіть суть звернення' },
            { min: 10, message: 'Опис має містити мінімум 10 символів' },
          ]}
        >
          <TextArea
            rows={6}
            placeholder="Детальний опис звернення..."
            showCount
            maxLength={2000}
          />
        </Form.Item>

        {/* Завантаження файлів */}
        <Form.Item label="Файли (опціонально)">
          <Upload
            beforeUpload={beforeUpload}
            onChange={handleChange}
            fileList={fileList}
            onRemove={handleRemoveFile}
            multiple
            accept={ALLOWED_EXTENSIONS.join(',')}
            showUploadList={{
              showPreviewIcon: false,
              showRemoveIcon: true,
              removeIcon: <DeleteOutlined />,
            }}
          >
            <Button icon={<UploadOutlined />} disabled={loading}>
              Обрати файли
            </Button>
          </Upload>
          <div style={{ marginTop: 8, color: '#8c8c8c', fontSize: 12 }}>
            Дозволені типи: PDF, DOC, DOCX, XLS, XLSX, JPG, PNG (максимум 10MB на файл)
          </div>
          
          {fileList.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <Typography.Text strong>Обрані файли ({fileList.length}):</Typography.Text>
              <ul style={{ marginTop: 8 }}>
                {fileList.map((file) => (
                  <li key={file.uid} style={{ marginBottom: 4 }}>
                    <FileOutlined /> {file.name}{' '}
                    <span style={{ color: '#8c8c8c' }}>
                      ({(file.size! / 1024).toFixed(2)} KB)
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </Form.Item>

        {/* Кнопки */}
        <Form.Item style={{ marginTop: 24 }}>
          <Space>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              size="large"
            >
              Створити звернення
            </Button>
            {onCancel && (
              <Button onClick={onCancel} disabled={loading} size="large">
                Скасувати
              </Button>
            )}
          </Space>
        </Form.Item>
      </Form>
    </div>
  );
};

export default CreateCaseForm;
