/**
 * Case Detail Page
 * Ohmatdyt CRM - Детальна картка звернення
 */

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import {
  Card,
  Descriptions,
  Tag,
  Typography,
  Timeline,
  List,
  Button,
  Space,
  Upload,
  message,
  Divider,
  Row,
  Col,
  Spin,
  Alert,
} from 'antd';
import {
  DownloadOutlined,
  FileOutlined,
  ArrowLeftOutlined,
  ClockCircleOutlined,
  UserOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { AuthGuard } from '@/components/Auth';
import { useAppSelector } from '@/store/hooks';
import { selectUser } from '@/store/slices/authSlice';
import { CaseStatus } from '@/store/slices/casesSlice';
import { TakeCaseButton, ChangeStatusForm, AddCommentForm } from '@/components/Cases';
import api from '@/lib/api';

const { Title, Text, Paragraph } = Typography;

// Типи для детальної інформації
interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: 'OPERATOR' | 'EXECUTOR' | 'ADMIN';
}

interface Category {
  id: string;
  name: string;
}

interface Channel {
  id: string;
  name: string;
}

interface StatusHistory {
  id: string;
  old_status: CaseStatus | null;
  new_status: CaseStatus;
  changed_at: string;
  changed_by: User;
}

interface Comment {
  id: string;
  text: string;
  is_internal: boolean;
  created_at: string;
  author: User;
}

interface Attachment {
  id: string;
  file_path: string;
  original_name: string;
  size_bytes: number;
  mime_type: string;
  created_at: string;
  uploaded_by: User;
}

interface CaseDetail {
  id: string;
  public_id: number;
  category: Category;
  channel: Channel;
  subcategory?: string;
  applicant_name: string;
  applicant_phone?: string;
  applicant_email?: string;
  summary: string;
  status: CaseStatus;
  author: User;
  responsible?: User;
  created_at: string;
  updated_at: string;
  status_history: StatusHistory[];
  comments: Comment[];
  attachments: Attachment[];
}

// Статуси з українськими назвами
const statusLabels: Record<CaseStatus, string> = {
  NEW: 'Новий',
  IN_PROGRESS: 'В роботі',
  NEEDS_INFO: 'Потрібна інформація',
  REJECTED: 'Відхилено',
  DONE: 'Виконано',
};

// Кольори для статусів
const statusColors: Record<CaseStatus, string> = {
  NEW: 'blue',
  IN_PROGRESS: 'orange',
  NEEDS_INFO: 'red',
  REJECTED: 'red',
  DONE: 'green',
};

const CaseDetailPage: React.FC = () => {
  const router = useRouter();
  const { id } = router.query;
  const user = useAppSelector(selectUser);

  const [caseDetail, setCaseDetail] = useState<CaseDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Функція для завантаження деталей звернення
  const fetchCaseDetail = async () => {
    if (!id || !user) return;

    setLoading(true);
    setError(null);
    try {
      const response = await api.get(`/api/cases/${id}`);
      setCaseDetail(response.data);
    } catch (err: any) {
      console.error('Failed to load case details:', err);
      setError(err.response?.data?.detail || 'Помилка завантаження деталей звернення');
    } finally {
      setLoading(false);
    }
  };

  // Завантаження деталей звернення
  useEffect(() => {
    fetchCaseDetail();
  }, [id, user]);

  // Обробка завантаження файлу
  const handleDownload = async (attachment: Attachment) => {
    try {
      const response = await api.get(`/api/attachments/${attachment.id}/download`, {
        responseType: 'blob',
      });

      // Створення посилання для завантаження
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', attachment.original_name);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      message.success('Файл завантажено');
    } catch (err: any) {
      console.error('Download failed:', err);
      message.error('Помилка завантаження файлу');
    }
  };

  // Форматування розміру файлу
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  // Перевірка доступу до внутрішніх коментарів
  const canViewInternalComments = (userRole: string | undefined): boolean => {
    return userRole === 'EXECUTOR' || userRole === 'ADMIN';
  };

  if (loading) {
    return (
      <AuthGuard>
        <div style={{ textAlign: 'center', padding: '100px 0' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>Завантаження...</div>
        </div>
      </AuthGuard>
    );
  }

  if (error || !caseDetail) {
    return (
      <AuthGuard>
        <div style={{ padding: '24px' }}>
          <Alert
            message="Помилка"
            description={error || 'Звернення не знайдено'}
            type="error"
            showIcon
          />
          <Button
            type="primary"
            icon={<ArrowLeftOutlined />}
            onClick={() => router.push('/cases')}
            style={{ marginTop: 16 }}
          >
            Повернутись до списку
          </Button>
        </div>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
        <div style={{ padding: '24px' }}>
          {/* Header */}
          <div style={{ marginBottom: 24 }}>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => router.push('/cases')}
              style={{ marginBottom: 16 }}
            >
              Назад до списку
            </Button>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Title level={2} style={{ margin: 0 }}>
                Звернення #{caseDetail.public_id}
                <Tag
                  color={statusColors[caseDetail.status]}
                  style={{ marginLeft: 16, fontSize: 16 }}
                >
                  {statusLabels[caseDetail.status]}
                </Tag>
              </Title>
              
              {/* Кнопки дій виконавця */}
              {user?.role === 'EXECUTOR' && (
                <Space size="middle">
                  <TakeCaseButton
                    caseId={caseDetail.id}
                    casePublicId={caseDetail.public_id}
                    currentStatus={caseDetail.status}
                    onSuccess={fetchCaseDetail}
                  />
                  <ChangeStatusForm
                    caseId={caseDetail.id}
                    casePublicId={caseDetail.public_id}
                    currentStatus={caseDetail.status}
                    onSuccess={fetchCaseDetail}
                  />
                </Space>
              )}
            </div>
          </div>

          <Row gutter={[24, 24]}>
            {/* Основні деталі */}
            <Col xs={24} lg={12}>
              <Card title="Основна інформація" bordered={false}>
                <Descriptions column={1} bordered size="small">
                  <Descriptions.Item label="Категорія">
                    {caseDetail.category.name}
                  </Descriptions.Item>
                  {caseDetail.subcategory && (
                    <Descriptions.Item label="Підкатегорія">
                      {caseDetail.subcategory}
                    </Descriptions.Item>
                  )}
                  <Descriptions.Item label="Канал звернення">
                    {caseDetail.channel.name}
                  </Descriptions.Item>
                  <Descriptions.Item label="Дата створення">
                    {dayjs(caseDetail.created_at).format('DD.MM.YYYY HH:mm')}
                  </Descriptions.Item>
                  <Descriptions.Item label="Останнє оновлення">
                    {dayjs(caseDetail.updated_at).format('DD.MM.YYYY HH:mm')}
                  </Descriptions.Item>
                  <Descriptions.Item label="Автор">
                    <Space>
                      <UserOutlined />
                      {caseDetail.author.full_name} ({caseDetail.author.username})
                    </Space>
                  </Descriptions.Item>
                  <Descriptions.Item label="Відповідальний">
                    {caseDetail.responsible ? (
                      <Space>
                        <UserOutlined />
                        {caseDetail.responsible.full_name} ({caseDetail.responsible.username})
                      </Space>
                    ) : (
                      <Text type="secondary">Не призначено</Text>
                    )}
                  </Descriptions.Item>
                </Descriptions>
              </Card>
            </Col>

            {/* Інформація про заявника */}
            <Col xs={24} lg={12}>
              <Card title="Інформація про заявника" bordered={false}>
                <Descriptions column={1} bordered size="small">
                  <Descriptions.Item label="Ім'я">
                    {caseDetail.applicant_name}
                  </Descriptions.Item>
                  {caseDetail.applicant_phone && (
                    <Descriptions.Item label="Телефон">
                      <a href={`tel:${caseDetail.applicant_phone}`}>
                        {caseDetail.applicant_phone}
                      </a>
                    </Descriptions.Item>
                  )}
                  {caseDetail.applicant_email && (
                    <Descriptions.Item label="Email">
                      <a href={`mailto:${caseDetail.applicant_email}`}>
                        {caseDetail.applicant_email}
                      </a>
                    </Descriptions.Item>
                  )}
                </Descriptions>

                <Divider />

                <div>
                  <Text strong>Суть звернення:</Text>
                  <Paragraph style={{ marginTop: 8, whiteSpace: 'pre-wrap' }}>
                    {caseDetail.summary}
                  </Paragraph>
                </div>
              </Card>
            </Col>

            {/* Історія статусів */}
            <Col xs={24} lg={12}>
              <Card
                title={
                  <Space>
                    <ClockCircleOutlined />
                    Історія статусів
                  </Space>
                }
                bordered={false}
              >
                {caseDetail.status_history.length > 0 ? (
                  <Timeline>
                    {caseDetail.status_history.map((history) => (
                      <Timeline.Item
                        key={history.id}
                        color={statusColors[history.new_status]}
                      >
                        <div>
                          <Text strong>
                            {history.old_status ? (
                              <>
                                {statusLabels[history.old_status]} → {statusLabels[history.new_status]}
                              </>
                            ) : (
                              <>Створено: {statusLabels[history.new_status]}</>
                            )}
                          </Text>
                        </div>
                        <div>
                          <Text type="secondary">
                            {dayjs(history.changed_at).format('DD.MM.YYYY HH:mm')}
                          </Text>
                        </div>
                        <div>
                          <Text type="secondary">
                            {history.changed_by.full_name}
                          </Text>
                        </div>
                      </Timeline.Item>
                    ))}
                  </Timeline>
                ) : (
                  <Text type="secondary">Немає історії змін статусу</Text>
                )}
              </Card>
            </Col>

            {/* Вкладення */}
            <Col xs={24} lg={12}>
              <Card
                title={
                  <Space>
                    <FileOutlined />
                    Вкладення ({caseDetail.attachments.length})
                  </Space>
                }
                bordered={false}
              >
                {caseDetail.attachments.length > 0 ? (
                  <List
                    dataSource={caseDetail.attachments}
                    renderItem={(attachment) => (
                      <List.Item
                        key={attachment.id}
                        actions={[
                          <Button
                            key="download"
                            type="link"
                            icon={<DownloadOutlined />}
                            onClick={() => handleDownload(attachment)}
                          >
                            Завантажити
                          </Button>,
                        ]}
                      >
                        <List.Item.Meta
                          avatar={<FileTextOutlined style={{ fontSize: 24 }} />}
                          title={attachment.original_name}
                          description={
                            <Space split="|">
                              <Text type="secondary">{formatFileSize(attachment.size_bytes)}</Text>
                              <Text type="secondary">
                                {dayjs(attachment.created_at).format('DD.MM.YYYY HH:mm')}
                              </Text>
                              <Text type="secondary">
                                {attachment.uploaded_by.full_name}
                              </Text>
                            </Space>
                          }
                        />
                      </List.Item>
                    )}
                  />
                ) : (
                  <Text type="secondary">Немає вкладень</Text>
                )}
              </Card>
            </Col>

            {/* Коментарі */}
            <Col xs={24}>
              {/* Форма додавання коментаря */}
              <AddCommentForm
                caseId={caseDetail.id}
                casePublicId={caseDetail.public_id}
                userRole={user?.role}
                onSuccess={fetchCaseDetail}
              />

              {/* Список коментарів */}
              <Card title="Коментарі" bordered={false}>
                {caseDetail.comments.length > 0 ? (
                  <List
                    dataSource={caseDetail.comments.filter((comment) => {
                      // Фільтруємо внутрішні коментарі для неавторизованих ролей
                      if (comment.is_internal) {
                        return canViewInternalComments(user?.role);
                      }
                      return true;
                    })}
                    renderItem={(comment) => (
                      <List.Item key={comment.id}>
                        <List.Item.Meta
                          avatar={<UserOutlined style={{ fontSize: 24 }} />}
                          title={
                            <Space>
                              <Text strong>{comment.author.full_name}</Text>
                              <Text type="secondary">
                                {dayjs(comment.created_at).format('DD.MM.YYYY HH:mm')}
                              </Text>
                              {comment.is_internal && (
                                <Tag color="orange">Внутрішній</Tag>
                              )}
                            </Space>
                          }
                          description={
                            <Paragraph style={{ marginTop: 8, whiteSpace: 'pre-wrap' }}>
                              {comment.text}
                            </Paragraph>
                          }
                        />
                      </List.Item>
                    )}
                  />
                ) : (
                  <Text type="secondary">Немає коментарів</Text>
                )}
              </Card>
            </Col>
          </Row>
        </div>
    </AuthGuard>
  );
};

export default CaseDetailPage;
