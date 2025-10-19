/**
 * Redux Store Configuration
 *
 * Central store configuration using Redux Toolkit.
 * Configures root reducer, middleware, and typed hooks.
 */

import { configureStore, combineReducers } from '@reduxjs/toolkit';
import { useDispatch, useSelector, type TypedUseSelectorHook } from 'react-redux';
import { themeReducer } from './slices';
import { themeMiddleware } from './middleware';

// Combine all reducers
export const rootReducer = combineReducers({
  theme: themeReducer,
});

// Configure the store
export const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types if needed
        ignoredActions: [],
      },
    }).concat(themeMiddleware),
});

// Infer types from the store
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Typed hooks for use throughout the app
export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
