/**
 * Modelos de domínio para API
 * Define as interfaces genéricas relacionadas às chamadas de API
 */

/**
 * Interface base para respostas de API
 */
export interface ApiResponse<T = any> {
  data: T
  message?: string
  status: number
}

/**
 * Interface para respostas de erro da API
 */
export interface ApiError {
  detail: string
  status: number
  message?: string
}

/**
 * Interface para paginação
 */
export interface PaginationParams {
  skip: number
  limit: number
}

/**
 * Interface para resposta paginada
 */
export interface PaginatedResponse<T> {
  data: T[]
  count: number
  skip: number
  limit: number
}

/**
 * Interface para configuração da API
 */
export interface ApiConfig {
  baseUrl: string
  timeout: number
  headers?: Record<string, string>
}
