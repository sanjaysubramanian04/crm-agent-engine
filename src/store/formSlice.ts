import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface FormState {
  id: number | null;
  hcpName: string;
  interactionType: string;
  date: string;
  time: string;
  attendees: string;
  topicsDiscussed: string;
  materialsShared: string;
  sentiment: 'Positive' | 'Neutral' | 'Negative' | '';
  outcomes: string;
  followUpActions: string;
  nextBestAction: string;
  pendingChanges: Record<string, string> | null;
}

const initialState: FormState = {
  id: null,
  hcpName: '',
  interactionType: '',
  date: '',
  time: '',
  attendees: '',
  topicsDiscussed: '',
  materialsShared: '',
  sentiment: '',
  outcomes: '',
  followUpActions: '',
  nextBestAction: '',
  pendingChanges: null,
};

const formSlice = createSlice({
  name: 'form',
  initialState,
  reducers: {
    updateFormState: (state, action: PayloadAction<Partial<FormState>>) => {
      // Functional requirement: Dynamic merge
      return { ...state, ...action.payload };
    },
    resetForm: () => initialState,
  },
});

export const { updateFormState, resetForm } = formSlice.actions;
export default formSlice.reducer;
