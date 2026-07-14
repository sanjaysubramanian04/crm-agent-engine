import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';
import { RootState } from './index';
import { updateFormState } from './formSlice';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}

const initialState: ChatState = {
  messages: [],
  isLoading: false,
  error: null,
};

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async (text: string, { getState, dispatch }) => {
    const state = getState() as RootState;
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: text,
        history: state.chat.messages,
        formState: state.form,
      }),
    });

    if (!response.ok) throw new Error('Failed to send message');
    const data = await response.json();

    // Update form state if provided
    if (data.formState) {
      dispatch(updateFormState({ ...data.formState, nextBestAction: data.nextBestAction }));
    }

    return data.messages;
  }
);

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<Message>) => {
      state.messages.push(action.payload);
    },
    clearChat: (state) => {
      state.messages = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(sendMessage.fulfilled, (state, action: PayloadAction<any[]>) => {
        state.isLoading = false;
        // Filter out tool internal messages for UI
        const filtered = action.payload.filter(m => !m.content.startsWith('[Tool:'));
        const lastAssistant = [...filtered].reverse().find(m => m.role === 'assistant');
        if (lastAssistant) {
          state.messages.push({ role: 'assistant', content: lastAssistant.content });
        } else {
          state.messages.push({ role: 'assistant', content: "Processed." });
        }
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Error';
      });
  },
});

export const { addMessage, clearChat } = chatSlice.actions;
export default chatSlice.reducer;
