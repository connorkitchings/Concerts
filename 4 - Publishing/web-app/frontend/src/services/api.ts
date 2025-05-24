import axios, { AxiosError, AxiosResponse } from 'axios';
import { Band, NextShow, PredictionResponse, ApiError } from '../types';

// API base URL - will be replaced with actual API URL in production
const API_BASE_URL = 'http://localhost:8000/api';

// Axios instance with common config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Fetches all available bands from the API.
 * 
 * @returns {Promise<Band[]>} Array of band objects
 * @throws {Error} If the API request fails
 */
export const getBands = async (): Promise<Band[]> => {
  try {
    const response: AxiosResponse<Band[]> = await api.get('/bands');
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>;
    throw new Error(
      axiosError.response?.data?.detail || 'Failed to fetch bands'
    );
  }
};

/**
 * Fetches information about a specific band.
 * 
 * @param {string} bandId - The band identifier
 * @returns {Promise<Band>} Band information
 * @throws {Error} If the API request fails
 */
export const getBand = async (bandId: string): Promise<Band> => {
  try {
    const response: AxiosResponse<Band> = await api.get(`/bands/${bandId}`);
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>;
    throw new Error(
      axiosError.response?.data?.detail || `Failed to fetch band ${bandId}`
    );
  }
};

/**
 * Fetches information about the next show for a band.
 * 
 * @param {string} bandId - The band identifier
 * @returns {Promise<NextShow>} Next show information
 * @throws {Error} If the API request fails
 */
export const getNextShow = async (bandId: string): Promise<NextShow> => {
  try {
    const response: AxiosResponse<NextShow> = await api.get(`/bands/${bandId}/next-show`);
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>;
    throw new Error(
      axiosError.response?.data?.detail || `Failed to fetch next show for ${bandId}`
    );
  }
};

/**
 * Fetches predictions for a specific band.
 * 
 * @param {string} bandId - The band identifier
 * @param {string} predictionType - Type of prediction ('notebook' or 'ckplus')
 * @param {number} limit - Number of predictions to return (default: 50)
 * @returns {Promise<PredictionResponse>} Prediction data and metadata
 * @throws {Error} If the API request fails
 */
export const getPredictions = async (
  bandId: string,
  predictionType: 'notebook' | 'ckplus',
  limit: number = 50
): Promise<PredictionResponse> => {
  try {
    const response: AxiosResponse<PredictionResponse> = await api.get(
      `/predictions/${bandId}/${predictionType}`,
      { params: { limit } }
    );
    return response.data;
  } catch (error) {
    const axiosError = error as AxiosError<ApiError>;
    throw new Error(
      axiosError.response?.data?.detail || `Failed to fetch predictions for ${bandId}`
    );
  }
};
