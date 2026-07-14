import { configureStore } from '@reduxjs/toolkit';
import formReducer from './formSlice';
import chatReducer from './chatSlice';

export const store = configureStore({
  reducer: {
    form: formReducer,
    chat: chatReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
