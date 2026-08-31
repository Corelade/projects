import { configureStore } from '@reduxjs/toolkit'
import { setupListeners } from '@reduxjs/toolkit/query'
import { useDispatch, useSelector } from 'react-redux'

import { baseApi } from './api/base-api'
import authReducer, { hydrate } from './slices/auth-slice'
import uiReducer from './slices/ui-slice'

// Side-effect imports: each injects its endpoints into baseApi.
import './api/staff-api'
import './api/departments-api'
import './api/schedule-api'
import './api/auth-api'

export const store = configureStore({
  reducer: {
    [baseApi.reducerPath]: baseApi.reducer,
    auth: authReducer,
    ui: uiReducer,
  },
  middleware: (getDefault) => getDefault().concat(baseApi.middleware),
})

// Read the stored session back before the first render, so RequireAuth sees a
// hydrated store and a reload on a protected route doesn't flash the sign-in page.
store.dispatch(hydrate())

setupListeners(store.dispatch)

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch

export const useAppDispatch = useDispatch.withTypes<AppDispatch>()
export const useAppSelector = useSelector.withTypes<RootState>()
