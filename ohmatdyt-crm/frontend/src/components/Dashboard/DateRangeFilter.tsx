/**
 * Date Range Filter Component
 * Ohmatdyt CRM - FE-301
 * 
 * Фільтр періоду для дашборду з RangePicker та швидкими пресетами
 */

import React from 'react';
import { DatePicker, Button, Space, Card } from 'antd';
import { CalendarOutlined, ReloadOutlined } from '@ant-design/icons';
import dayjs, { Dayjs } from 'dayjs';
import { DateRangeFilter as DateRangeFilterType } from '@/types/dashboard';

const { RangePicker } = DatePicker;

interface DateRangeFilterProps {
  value: DateRangeFilterType;
  onChange: (dateRange: DateRangeFilterType) => void;
  onApply: () => void;
}

const DateRangeFilter: React.FC<DateRangeFilterProps> = ({
  value,
  onChange,
  onApply,
}) => {
  // Конвертація з ISO string в Dayjs
  const getDayjsRange = (): [Dayjs | null, Dayjs | null] => {
    const start = value.date_from ? dayjs(value.date_from) : null;
    const end = value.date_to ? dayjs(value.date_to) : null;
    return [start, end];
  };

  // Обробка зміни дат
  const handleRangeChange = (dates: [Dayjs | null, Dayjs | null] | null) => {
    if (!dates) {
      onChange({ date_from: null, date_to: null });
      return;
    }

    const [start, end] = dates;
    onChange({
      date_from: start ? start.startOf('day').toISOString() : null,
      date_to: end ? end.endOf('day').toISOString() : null,
    });
  };

  // Швидкі пресети
  const setToday = () => {
    const today = dayjs().startOf('day');
    onChange({
      date_from: today.toISOString(),
      date_to: dayjs().endOf('day').toISOString(),
    });
  };

  const setThisWeek = () => {
    const start = dayjs().startOf('week');
    const end = dayjs().endOf('week');
    onChange({
      date_from: start.toISOString(),
      date_to: end.toISOString(),
    });
  };

  const setThisMonth = () => {
    const start = dayjs().startOf('month');
    const end = dayjs().endOf('month');
    onChange({
      date_from: start.toISOString(),
      date_to: end.toISOString(),
    });
  };

  const setLast7Days = () => {
    const end = dayjs().endOf('day');
    const start = dayjs().subtract(7, 'days').startOf('day');
    onChange({
      date_from: start.toISOString(),
      date_to: end.toISOString(),
    });
  };

  const setLast30Days = () => {
    const end = dayjs().endOf('day');
    const start = dayjs().subtract(30, 'days').startOf('day');
    onChange({
      date_from: start.toISOString(),
      date_to: end.toISOString(),
    });
  };

  const clearFilter = () => {
    onChange({ date_from: null, date_to: null });
  };

  return (
    <Card
      size="small"
      style={{ marginBottom: 24 }}
      title={
        <span>
          <CalendarOutlined style={{ marginRight: 8 }} />
          Фільтр періоду
        </span>
      }
    >
      <Space wrap size="small">
        {/* Range Picker */}
        <RangePicker
          value={getDayjsRange()}
          onChange={handleRangeChange}
          format="DD.MM.YYYY"
          placeholder={['Від', 'До']}
          style={{ width: 250 }}
        />

        {/* Швидкі пресети */}
        <Button size="small" onClick={setToday}>
          Сьогодні
        </Button>
        <Button size="small" onClick={setThisWeek}>
          Цей тиждень
        </Button>
        <Button size="small" onClick={setThisMonth}>
          Цей місяць
        </Button>
        <Button size="small" onClick={setLast7Days}>
          Останні 7 днів
        </Button>
        <Button size="small" onClick={setLast30Days}>
          Останні 30 днів
        </Button>

        {/* Кнопки дії */}
        <Button
          type="primary"
          icon={<CalendarOutlined />}
          onClick={onApply}
        >
          Застосувати
        </Button>
        <Button
          icon={<ReloadOutlined />}
          onClick={() => {
            clearFilter();
            onApply();
          }}
        >
          Скинути
        </Button>
      </Space>
    </Card>
  );
};

export default DateRangeFilter;
