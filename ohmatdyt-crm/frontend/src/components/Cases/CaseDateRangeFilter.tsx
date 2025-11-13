/**
 * Case Date Range Filter Component
 * Ohmatdyt CRM - FE-015
 * 
 * Компонент фільтру періоду дат з пресетами всередині випадаючого меню календаря
 */

import React from 'react';
import { DatePicker } from 'antd';
import dayjs, { Dayjs } from 'dayjs';
import type { RangePickerProps } from 'antd/es/date-picker';

const { RangePicker } = DatePicker;

interface CaseDateRangeFilterProps {
  value?: [Dayjs, Dayjs] | undefined;
  onChange: (dates: [Dayjs, Dayjs] | undefined) => void;
}

/**
 * Компонент для фільтрації звернень за датою створення
 * Пресети відображаються всередині випадаючого меню календаря
 */
const CaseDateRangeFilter: React.FC<CaseDateRangeFilterProps> = ({
  value,
  onChange,
}) => {
  
  // Обробка зміни дат через календар
  const handleRangeChange: RangePickerProps['onChange'] = (dates) => {
    if (!dates || !dates[0] || !dates[1]) {
      onChange(undefined);
      return;
    }

    onChange([
      dates[0].startOf('day'),
      dates[1].endOf('day'),
    ]);
  };

  // Швидкі пресети для RangePicker (відображаються у випадаючому меню)
  const rangePresets: RangePickerProps['presets'] = [
    {
      label: 'Сьогодні',
      value: [dayjs().startOf('day'), dayjs().endOf('day')],
    },
    {
      label: 'Вчора',
      value: [
        dayjs().subtract(1, 'day').startOf('day'),
        dayjs().subtract(1, 'day').endOf('day'),
      ],
    },
    {
      label: 'Вчора+сьогодні',
      value: [
        dayjs().subtract(1, 'day').startOf('day'),
        dayjs().endOf('day'),
      ],
    },
    {
      label: 'Останні 7 днів',
      value: [
        dayjs().subtract(6, 'days').startOf('day'),
        dayjs().endOf('day'),
      ],
    },
    {
      label: 'Поточний тиждень',
      value: [
        dayjs().startOf('week'),
        dayjs().endOf('week'),
      ],
    },
    {
      label: 'Попередній тиждень',
      value: [
        dayjs().subtract(1, 'week').startOf('week'),
        dayjs().subtract(1, 'week').endOf('week'),
      ],
    },
  ];

  return (
    <RangePicker
      value={value}
      onChange={handleRangeChange}
      format="DD.MM.YYYY"
      placeholder={['Від', 'До']}
      presets={rangePresets}
      style={{ width: '100%' }}
    />
  );
};

export default CaseDateRangeFilter;
