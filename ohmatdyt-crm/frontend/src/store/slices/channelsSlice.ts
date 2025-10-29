/**
 * Channels Redux Slice
 * Ohmatdyt CRM - Управління каналами зв'язку
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Типи
export interface Channel {
  id: string;
  name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateChannelData {
  name: string;
}

export interface UpdateChannelData {
  name: string;
}

export interface ChannelsState {
  channels: Channel[];
  total: number;
  currentChannel: Channel | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: ChannelsState = {
  channels: [],
  total: 0,
  currentChannel: null,
  isLoading: false,
  error: null,
};

// Async Thunks

/**
 * Отримання списку каналів з фільтрами
 */
export const fetchChannelsAsync = createAsyncThunk(
  'channels/fetchChannels',
  async (params: {
    skip?: number;
    limit?: number;
    search?: string;
    include_inactive?: boolean;
  } = {}) => {
    const token = localStorage.getItem('access_token');
    const response = await axios.get(`${API_URL}/api/channels`, {
      params,
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  }
);

/**
 * Отримання каналу за ID
 */
export const fetchChannelByIdAsync = createAsyncThunk(
  'channels/fetchChannelById',
  async (id: string) => {
    const token = localStorage.getItem('access_token');
    const response = await axios.get(`${API_URL}/api/channels/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  }
);

/**
 * Створення нового каналу
 */
export const createChannelAsync = createAsyncThunk(
  'channels/createChannel',
  async (data: CreateChannelData, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.post(`${API_URL}/api/channels`, data, {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 400 && error.response?.data?.detail?.includes('already exists')) {
        return rejectWithValue('Канал з такою назвою вже існує');
      }
      return rejectWithValue(error.response?.data?.detail || 'Помилка при створенні каналу');
    }
  }
);

/**
 * Оновлення каналу (PUT)
 */
export const updateChannelAsync = createAsyncThunk(
  'channels/updateChannel',
  async ({ id, data }: { id: string; data: UpdateChannelData }, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.put(`${API_URL}/api/channels/${id}`, data, {
        headers: { Authorization: `Bearer ${token}` },
      });
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 400 && error.response?.data?.detail?.includes('already exists')) {
        return rejectWithValue('Канал з такою назвою вже існує');
      }
      return rejectWithValue(error.response?.data?.detail || 'Помилка при оновленні каналу');
    }
  }
);

/**
 * Деактивація каналу
 */
export const deactivateChannelAsync = createAsyncThunk(
  'channels/deactivateChannel',
  async (id: string, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        return rejectWithValue('Не знайдено токен автентифікації. Будь ласка, увійдіть знову.');
      }
      const response = await axios.post(
        `${API_URL}/api/channels/${id}/deactivate`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 401) {
        return rejectWithValue('Сесія застаріла. Будь ласка, увійдіть знову.');
      }
      return rejectWithValue(error.response?.data?.detail || 'Помилка при деактивації каналу');
    }
  }
);

/**
 * Активація каналу
 */
export const activateChannelAsync = createAsyncThunk(
  'channels/activateChannel',
  async (id: string, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        return rejectWithValue('Не знайдено токен автентифікації. Будь ласка, увійдіть знову.');
      }
      const response = await axios.post(
        `${API_URL}/api/channels/${id}/activate`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 401) {
        return rejectWithValue('Сесія застаріла. Будь ласка, увійдіть знову.');
      }
      return rejectWithValue(error.response?.data?.detail || 'Помилка при активації каналу');
    }
  }
);

// Slice
const channelsSlice = createSlice({
  name: 'channels',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearCurrentChannel: (state) => {
      state.currentChannel = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch Channels
    builder.addCase(fetchChannelsAsync.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(fetchChannelsAsync.fulfilled, (state, action) => {
      state.isLoading = false;
      // API повертає { channels: [...], total: N }
      state.channels = action.payload.channels || [];
      state.total = action.payload.total || 0;
    });
    builder.addCase(fetchChannelsAsync.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.error.message || 'Помилка при завантаженні каналів';
    });

    // Fetch Channel By ID
    builder.addCase(fetchChannelByIdAsync.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(fetchChannelByIdAsync.fulfilled, (state, action) => {
      state.isLoading = false;
      state.currentChannel = action.payload;
    });
    builder.addCase(fetchChannelByIdAsync.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.error.message || 'Помилка при завантаженні каналу';
    });

    // Create Channel
    builder.addCase(createChannelAsync.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(createChannelAsync.fulfilled, (state, action) => {
      state.isLoading = false;
      state.channels.unshift(action.payload);
      state.total += 1;
    });
    builder.addCase(createChannelAsync.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string || 'Помилка при створенні каналу';
    });

    // Update Channel
    builder.addCase(updateChannelAsync.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(updateChannelAsync.fulfilled, (state, action) => {
      state.isLoading = false;
      const index = state.channels.findIndex((ch) => ch.id === action.payload.id);
      if (index !== -1) {
        state.channels[index] = action.payload;
      }
      if (state.currentChannel?.id === action.payload.id) {
        state.currentChannel = action.payload;
      }
    });
    builder.addCase(updateChannelAsync.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string || 'Помилка при оновленні каналу';
    });

    // Deactivate Channel
    builder.addCase(deactivateChannelAsync.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(deactivateChannelAsync.fulfilled, (state, action) => {
      state.isLoading = false;
      const index = state.channels.findIndex((ch) => ch.id === action.payload.id);
      if (index !== -1) {
        state.channels[index] = action.payload;
      }
    });
    builder.addCase(deactivateChannelAsync.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string || 'Помилка при деактивації каналу';
    });

    // Activate Channel
    builder.addCase(activateChannelAsync.pending, (state) => {
      state.isLoading = true;
      state.error = null;
    });
    builder.addCase(activateChannelAsync.fulfilled, (state, action) => {
      state.isLoading = false;
      const index = state.channels.findIndex((ch) => ch.id === action.payload.id);
      if (index !== -1) {
        state.channels[index] = action.payload;
      }
    });
    builder.addCase(activateChannelAsync.rejected, (state, action) => {
      state.isLoading = false;
      state.error = action.payload as string || 'Помилка при активації каналу';
    });
  },
});

// Селектори
export const selectChannels = (state: any) => state.channels?.channels || [];
export const selectChannelsTotal = (state: any) => state.channels?.total || 0;
export const selectChannelsLoading = (state: any) => state.channels?.isLoading || false;
export const selectChannelsError = (state: any) => state.channels?.error || null;
export const selectCurrentChannel = (state: any) => state.channels?.currentChannel || null;

export const { clearError, clearCurrentChannel } = channelsSlice.actions;
export default channelsSlice.reducer;
