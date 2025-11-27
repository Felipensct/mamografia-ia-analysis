/**
 * Barrel exports para modelos de domínio
 * Centraliza todas as exportações de modelos em um local
 */

// Analysis models
export type {
  AnalysisStatus,
  Analysis,
  ImageInfo,
  AnalysisResults,
  AnalysisDetail,
  UploadResponse,
  AnalysisResponse
} from './analysis.model'

// API models
export type {
  ApiResponse,
  ApiError,
  PaginationParams,
  PaginatedResponse,
  ApiConfig
} from './api.model'
