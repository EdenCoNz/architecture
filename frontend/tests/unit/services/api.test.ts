/**
 * API Service Tests
 *
 * Test suite for the API service layer.
 * Tests network communication, error handling, and response formatting.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Unmock the API service for these unit tests (it's mocked globally in setup.ts)
vi.unmock('@/services/api');

import { apiService } from '@/services/api';
import type { HealthCheckResponse, ApiError, ThemePreferenceResponse } from '@/types';

describe('API Service', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    vi.resetAllMocks();
  });

  afterEach(() => {
    // Restore original fetch after each test
    vi.restoreAllMocks();
  });

  describe('getHealth', () => {
    it('should successfully fetch health check data', async () => {
      // Arrange - Mock successful response
      const mockHealthData: HealthCheckResponse = {
        status: 'healthy',
        timestamp: '2025-10-19T16:23:45.123456',
        version: '0.1.0',
        service: 'backend-api',
        database: {
          status: 'healthy',
          connected: true,
          engine: 'django.db.backends.postgresql',
        },
        debug_mode: true,
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockHealthData,
      } as Response);

      // Act
      const result = await apiService.getHealth();

      // Assert
      expect(result.status).toBe(200);
      expect(result.data).toEqual(mockHealthData);
      expect(result.data.status).toBe('healthy');
      expect(result.data.database.connected).toBe(true);
    });

    it('should call the correct endpoint URL', async () => {
      // Arrange
      const mockHealthData: HealthCheckResponse = {
        status: 'healthy',
        timestamp: '2025-10-19T16:23:45.123456',
        version: '0.1.0',
        service: 'backend-api',
        database: {
          status: 'healthy',
          connected: true,
          engine: 'django.db.backends.postgresql',
        },
        debug_mode: true,
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockHealthData,
      } as Response);

      // Act
      await apiService.getHealth();

      // Assert
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/health/',
        expect.objectContaining({
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        })
      );
    });

    it('should handle HTTP error responses (404)', async () => {
      // Arrange - Mock 404 response
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        statusText: 'Not Found',
      } as Response);

      // Act & Assert
      try {
        await apiService.getHealth();
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error).toMatchObject({
          message: expect.stringContaining('HTTP error'),
          status: 404,
        } as ApiError);
      }
    });

    it('should handle HTTP error responses (500)', async () => {
      // Arrange - Mock 500 response
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      } as Response);

      // Act & Assert
      try {
        await apiService.getHealth();
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error).toMatchObject({
          message: expect.stringContaining('HTTP error'),
          status: 500,
        } as ApiError);
      }
    });

    it('should handle network errors gracefully', async () => {
      // Arrange - Mock network error
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

      // Act & Assert
      try {
        await apiService.getHealth();
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error).toMatchObject({
          message: 'Network error',
          status: 0,
        } as ApiError);
      }
    });

    it('should handle timeout errors', async () => {
      // Arrange - Mock timeout (simulate AbortError)
      const abortError = new Error('Request timeout');
      abortError.name = 'AbortError';
      global.fetch = vi.fn().mockRejectedValue(abortError);

      // Act & Assert
      try {
        await apiService.getHealth();
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error).toMatchObject({
          message: 'Request timeout',
          status: 0,
        } as ApiError);
      }
    });

    it('should handle malformed JSON responses', async () => {
      // Arrange - Mock invalid JSON
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => {
          throw new SyntaxError('Unexpected token');
        },
      } as Response);

      // Act & Assert
      await expect(apiService.getHealth()).rejects.toThrow();
    });

    it('should include correct headers in request', async () => {
      // Arrange
      const mockHealthData: HealthCheckResponse = {
        status: 'healthy',
        timestamp: '2025-10-19T16:23:45.123456',
        version: '0.1.0',
        service: 'backend-api',
        database: {
          status: 'healthy',
          connected: true,
          engine: 'django.db.backends.postgresql',
        },
        debug_mode: true,
      };

      const fetchSpy = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockHealthData,
      } as Response);

      global.fetch = fetchSpy;

      // Act
      await apiService.getHealth();

      // Assert
      expect(fetchSpy).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        })
      );
    });

    it('should return response with correct structure', async () => {
      // Arrange
      const mockHealthData: HealthCheckResponse = {
        status: 'healthy',
        timestamp: '2025-10-19T16:23:45.123456',
        version: '0.1.0',
        service: 'backend-api',
        database: {
          status: 'healthy',
          connected: true,
          engine: 'django.db.backends.postgresql',
        },
        debug_mode: true,
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockHealthData,
      } as Response);

      // Act
      const result = await apiService.getHealth();

      // Assert
      expect(result).toHaveProperty('data');
      expect(result).toHaveProperty('status');
      expect(typeof result.status).toBe('number');
      expect(result.status).toBe(200);
    });

    it('should handle CORS errors', async () => {
      // Arrange - Mock CORS error
      global.fetch = vi.fn().mockRejectedValueOnce(new TypeError('Failed to fetch'));

      // Act & Assert
      await expect(apiService.getHealth()).rejects.toThrow();
    });
  });

  describe('getThemePreference', () => {
    it('should successfully fetch theme preference', async () => {
      // Arrange - Mock successful response
      const mockThemeData: ThemePreferenceResponse = {
        theme: 'dark',
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockThemeData,
      } as Response);

      // Act
      const result = await apiService.getThemePreference();

      // Assert
      expect(result.status).toBe(200);
      expect(result.data).toEqual(mockThemeData);
      expect(result.data.theme).toBe('dark');
    });

    it('should call the correct endpoint URL with credentials', async () => {
      // Arrange
      const mockThemeData: ThemePreferenceResponse = {
        theme: 'auto',
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockThemeData,
      } as Response);

      // Act
      await apiService.getThemePreference();

      // Assert
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/preferences/theme/',
        expect.objectContaining({
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
        })
      );
    });

    it('should handle 401 Unauthorized error', async () => {
      // Arrange - Mock 401 response
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
      } as Response);

      // Act & Assert
      try {
        await apiService.getThemePreference();
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error).toMatchObject({
          message: expect.stringContaining('HTTP error'),
          status: 401,
        } as ApiError);
      }
    });

    it('should handle different theme values', async () => {
      const themes: Array<'light' | 'dark' | 'auto'> = ['light', 'dark', 'auto'];

      for (const theme of themes) {
        // Arrange
        const mockThemeData: ThemePreferenceResponse = { theme };

        global.fetch = vi.fn().mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockThemeData,
        } as Response);

        // Act
        const result = await apiService.getThemePreference();

        // Assert
        expect(result.data.theme).toBe(theme);
      }
    });
  });

  describe('updateThemePreference', () => {
    it('should successfully update theme preference to dark', async () => {
      // Arrange
      const mockThemeData: ThemePreferenceResponse = {
        theme: 'dark',
      };

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockThemeData,
      } as Response);

      // Act
      const result = await apiService.updateThemePreference('dark');

      // Assert
      expect(result.status).toBe(200);
      expect(result.data.theme).toBe('dark');
    });

    it('should call PATCH endpoint with correct payload', async () => {
      // Arrange
      const mockThemeData: ThemePreferenceResponse = {
        theme: 'light',
      };

      const fetchSpy = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockThemeData,
      } as Response);

      global.fetch = fetchSpy;

      // Act
      await apiService.updateThemePreference('light');

      // Assert
      expect(fetchSpy).toHaveBeenCalledWith(
        'http://localhost:8000/api/preferences/theme/',
        expect.objectContaining({
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({ theme: 'light' }),
        })
      );
    });

    it('should send credentials with request', async () => {
      // Arrange
      const mockThemeData: ThemePreferenceResponse = {
        theme: 'auto',
      };

      const fetchSpy = vi.fn().mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockThemeData,
      } as Response);

      global.fetch = fetchSpy;

      // Act
      await apiService.updateThemePreference('auto');

      // Assert
      expect(fetchSpy).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          credentials: 'include',
        })
      );
    });

    it('should handle all theme mode values', async () => {
      const themes: Array<'light' | 'dark' | 'auto'> = ['light', 'dark', 'auto'];

      for (const theme of themes) {
        // Arrange
        const mockThemeData: ThemePreferenceResponse = { theme };
        const fetchSpy = vi.fn().mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockThemeData,
        } as Response);

        global.fetch = fetchSpy;

        // Act
        const result = await apiService.updateThemePreference(theme);

        // Assert
        expect(result.data.theme).toBe(theme);
        expect(fetchSpy).toHaveBeenCalledWith(
          expect.any(String),
          expect.objectContaining({
            body: JSON.stringify({ theme }),
          })
        );
      }
    });

    it('should handle 401 Unauthorized error on update', async () => {
      // Arrange - Mock 401 response
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
      } as Response);

      // Act & Assert
      try {
        await apiService.updateThemePreference('dark');
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error).toMatchObject({
          message: expect.stringContaining('HTTP error'),
          status: 401,
        } as ApiError);
      }
    });

    it('should handle network errors on update', async () => {
      // Arrange - Mock network error
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

      // Act & Assert
      try {
        await apiService.updateThemePreference('light');
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error).toMatchObject({
          message: 'Network error',
          status: 0,
        } as ApiError);
      }
    });
  });
});
