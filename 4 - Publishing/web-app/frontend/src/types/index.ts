// Band type
export interface Band {
  id: string;
  name: string;
  shortName: string;
  displayName: string;
}

// Song prediction type
export interface SongPrediction {
  name: string;
  times_played_last_year?: number;
  last_time_played?: string;
  current_gap?: number;
  average_gap?: number;
  median_gap?: number;
  probability?: number;
  features?: Record<string, any>;
}

// Next show information
export interface NextShow {
  date: string;
  venue?: string;
  city?: string;
  state?: string;
}

// Prediction response from API
export interface PredictionResponse {
  predictions: SongPrediction[];
  meta: {
    band: string;
    type: string;
    last_updated: string;
  };
}

// API error response
export interface ApiError {
  detail: string;
}
