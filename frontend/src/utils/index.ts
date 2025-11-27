/**
 * Barrel exports para utilitários
 * Centraliza todas as exportações de utilitários em um local
 */

// Formatters
export {
  formatFileSize,
  formatDate,
  getStatusBadgeClass,
  getStatusText,
  getStatusBadgeClassModern,
  getStatusGradient,
  getStatusDotClass
} from './formatters'

// Image utilities
export {
  IMAGE_PLACEHOLDER_SVG,
  handleImageError,
  formatImageDimensions,
  isValidImageFile,
  isValidFileSize,
  createImagePreview,
  revokeImagePreview
} from './image'

// Adapters
export {
  adaptAnalysis,
  adaptAnalyses,
  adaptUploadResponse,
  adaptAnalysisResponse
} from './adapters'
