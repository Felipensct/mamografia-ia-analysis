/**
 * Modelos de domínio para Analysis
 * Define as interfaces e tipos relacionados às análises de mamografia
 */

/**
 * Status possíveis para uma análise
 */
export type AnalysisStatus = 'uploaded' | 'processing' | 'completed' | 'error'

/**
 * Interface base para uma análise
 */
export interface Analysis {
  id: number
  filename: string
  original_filename: string
  file_size: number
  upload_date: string
  processing_date?: string
  status: AnalysisStatus
  is_processed: boolean
  has_analysis: boolean
  error_message?: string
  info?: ImageInfo
  results?: AnalysisResults
}

/**
 * Informações técnicas da imagem
 */
export interface ImageInfo {
  dimensions: [number, number]
  format: string
  mode: string
  is_optimized: boolean
  was_resized: boolean
  original_dimensions?: [number, number]
}

/**
 * Resultados das análises de IA
 */
export interface AnalysisResults {
  gemini?: string
  gpt4v?: string
}

/**
 * Interface completa para detalhes de uma análise
 */
export interface AnalysisDetail extends Analysis {
  info?: ImageInfo
  results: AnalysisResults
}

/**
 * Interface para resposta de upload
 */
export interface UploadResponse {
  message: string
  analysisId: number
  filename: string
  original_filename: string
  info: ImageInfo
  file_size: number
  status: string
}

/**
 * Interface para resposta de análise
 */
export interface AnalysisResponse {
  message: string
  analysisId: number
  filename: string
  status: string
  model?: string
  analysis?: string
}
