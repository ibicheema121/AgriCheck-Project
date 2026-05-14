import { get, post } from "./api";

export interface SensorReading {
  id: number;
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  ph: number;
  temperature: number;
  humidity: number;
  ec: number;
  timestamp: string;
}

export interface SensorReadingInput {
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  ph: number;
  temperature: number;
  humidity: number;
  ec: number;
}

export const sensorService = {
  /**
   * Get the latest sensor reading
   */
  getLatest: () => get<SensorReading>("/readings/latest"),

  /**
   * Get historical readings
   * @param limit Number of readings to fetch (default: 20, max: 100)
   */
  getHistory: (limit = 20) => 
    get<SensorReading[]>(`/readings/history?limit=${Math.min(limit, 100)}`),

  /**
   * Upload new sensor data
   */
  uploadReading: (data: SensorReadingInput) => 
    post<SensorReading>("/readings", data),
};

export default sensorService;
