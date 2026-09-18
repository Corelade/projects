import { createSlice, type PayloadAction } from '@reduxjs/toolkit'
import type { Staff } from '@/types'
import { currentWeekStart } from '@/lib/dates'
import { readStoredOpen, writeStoredOpen } from '@/components/ask-ai/chat-storage'

export interface Toast {
  id: string
  variant: 'success' | 'error' | 'info'
  message: string
}

export interface SortState {
  key: keyof Staff | 'name'
  dir: 'asc' | 'desc'
}

interface UiState {
  /** ISO Monday. Mirrored to ?week= by the schedule page. */
  selectedWeekStart: string
  // selectedWeekEnd: string
  staffSearch: string
  departmentSearch: string
  staffSort: SortState
  toasts: Toast[]
  /** AskAI side panel. Not route-derived: it floats over every app page. */
  askAiOpen: boolean
}

/**
 * Client-only state. Server data lives in RTK Query and is never copied here.
 * Drawer open/closed is deliberately absent — it derives from the route, so
 * Back closes the form and URLs stay shareable.
 */
const initialState: UiState = {
  selectedWeekStart: currentWeekStart(),
  // selectedWeekEnd: weekEnd(currentWeekStart()),
  staffSearch: '',
  departmentSearch: '',
  staffSort: { key: 'name', dir: 'asc' },
  toasts: [],
  askAiOpen: readStoredOpen(),
}

let toastSeq = 0

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setWeek(state, action: PayloadAction<string>) {
      state.selectedWeekStart = action.payload
    },
    setStaffSearch(state, action: PayloadAction<string>) {
      state.staffSearch = action.payload
    },
    setDepartmentSearch(state, action: PayloadAction<string>) {
      state.departmentSearch = action.payload
    },
    setStaffSort(state, action: PayloadAction<SortState>) {
      state.staffSort = action.payload
    },
    pushToast: {
      reducer(state, action: PayloadAction<Toast>) {
        state.toasts.push(action.payload)
        // Cap the stack at three (docs/ui/03-components.md).
        if (state.toasts.length > 3) state.toasts.shift()
      },
      prepare(variant: Toast['variant'], message: string) {
        return { payload: { id: `t${++toastSeq}`, variant, message } }
      },
    },
    dismissToast(state, action: PayloadAction<string>) {
      state.toasts = state.toasts.filter((t) => t.id !== action.payload)
    },
    toggleAskAi(state) {
      state.askAiOpen = !state.askAiOpen
      writeStoredOpen(state.askAiOpen)
    },
    setAskAiOpen(state, action: PayloadAction<boolean>) {
      state.askAiOpen = action.payload
      writeStoredOpen(state.askAiOpen)
    },
  },
})

export const {
  setWeek,
  setStaffSearch,
  setDepartmentSearch,
  setStaffSort,
  pushToast,
  dismissToast,
  toggleAskAi,
  setAskAiOpen,
} = uiSlice.actions

export default uiSlice.reducer
