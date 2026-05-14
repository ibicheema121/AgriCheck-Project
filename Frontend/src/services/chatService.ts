import { get, post } from "./api";

export interface ChatMessage {
  id?: number;
  role: "user" | "assistant";
  text: string;
  timestamp?: string;
}

export interface SensorData {
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  ph: number;
  temperature: number;
  humidity: number;
  ec: number;
}

// Public Chat Response
export interface PublicChatResponse {
  response: string;
  intent: "GENERAL_INFO" | "DETAIL_REQUIRED" | "OFF_TOPIC";
  requires_login: boolean;
  show_features: boolean;
  agricheck_features?: string;
  endpoint_info?: {
    public_endpoint: string;
    private_endpoint: string;
    auth_required_for_private: boolean;
    auth_type: string;
  };
}

// Authenticated Chat Request
export interface AdvisorChatRequest {
  message: string;
  session_id?: string;
  land_size_acres?: number;
  include_sensor_data?: boolean;
}

// Authenticated Chat Response
export interface AdvisorChatResponse {
  response: string;
  session_id: string;
  sensor_data_used?: SensorData;
  timestamp: string;
  recommendations?: unknown;
}

// Crop Recommendation Interfaces
export interface CropRecommendationItem {
  rank: number;
  name: string;
  reason: string;
}

export interface CropRecommendationResponse {
  status: string;
  sensor_data: SensorData & { reading_id: number; timestamp: string };
  recommendations: CropRecommendationItem[];
  summary: string;
}

export const chatService = {
  /**
   * Public chat endpoint - No authentication required
   * Used by dashboard and landing page
   */
  publicChat: (message: string, language: "en" | "ur" | "auto" = "auto") => 
    post<PublicChatResponse>("/api/v1/chat/public", { message, language }),

  /**
   * Authenticated advisor chat - Requires Firebase JWT
   * Includes sensor data integration and session management
   */
  advisorChat: (request: AdvisorChatRequest) => {
    const payload: Record<string, unknown> = {
      message: request.message,
      land_size_acres: request.land_size_acres ?? 1.0,
    };

    if (request.session_id) payload.session_id = request.session_id;
    if (request.include_sensor_data !== undefined) {
      payload.include_sensor_data = request.include_sensor_data;
    }

    return post<AdvisorChatResponse>("/chat/", payload);
  },

  /**
   * GET /api/v1/recommend-crops
   * Returns top-3 crop recommendations based on latest live sensor reading.
   */
  getCropRecommendations: () =>
    get<CropRecommendationResponse>("/api/v1/recommend-crops"),
};

export default chatService;
