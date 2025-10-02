import axios from 'axios'
import { API_CONFIG } from '@/config/api'

const API_BASE_URL = API_CONFIG.BASE_URL

export interface Analysis {
  id: number
  filename: string
  original_filename: string
  file_size: number
  upload_date: string
  processing_date?: string
  status: 'uploaded' | 'processing' | 'completed' | 'error'
  is_processed: boolean
  has_analysis: boolean
  error_message?: string
}

export interface AnalysisDetail extends Analysis {
  results: {
    gemini?: string
    gpt4v?: string
  }
}

export interface UploadResponse {
  message: string
  analysis_id: number
  filename: string
  original_filename: string
  info: {
    dimensions: [number, number]
    format: string
    mode: string
    is_optimized: boolean
  }
  file_size: number
  status: string
}

export interface AnalysisResponse {
  message: string
  analysis_id: number
  filename: string
  status: string
  model?: string
  analysis?: string
}

class ApiService {
  private api = axios.create({
    baseURL: API_BASE_URL,
    timeout: API_CONFIG.TIMEOUT,
  })

  constructor() {
    // Interceptor para logs de requisições
    this.api.interceptors.request.use(
      (config) => {
        console.log(`🚀 ${config.method?.toUpperCase()} ${config.url}`)
        return config
      },
      (error) => {
        console.error('❌ Erro na requisição:', error)
        return Promise.reject(error)
      }
    )

    // Interceptor para logs de respostas
    this.api.interceptors.response.use(
      (response) => {
        console.log(`✅ ${response.status} ${response.config.url}`)
        return response
      },
      (error) => {
        console.error('❌ Erro na resposta:', error.response?.data || error.message)
        return Promise.reject(error)
      }
    )
  }

  // Verificar saúde da API
  async checkHealth() {
    const response = await this.api.get('/health')
    return response.data
  }

  // Upload de imagem
  async uploadImage(file: File): Promise<UploadResponse> {
    console.log('📤 Iniciando upload:', {
      filename: file.name,
      size: file.size,
      type: file.type,
      apiUrl: API_BASE_URL
    })
    
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await this.api.post('/api/v1/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      
      console.log('✅ Upload bem-sucedido:', response.data)
      return response.data
    } catch (error: any) {
      console.error('❌ Erro no upload:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        config: error.config
      })
      throw error
    }
  }

  // Listar todas as análises
  async getAnalyses(skip = 0, limit = 10): Promise<{ analyses: Analysis[]; count: number }> {
    const response = await this.api.get('/api/v1/analyses', {
      params: { skip, limit },
    })
    return response.data
  }

  // Obter detalhes de uma análise específica
  async getAnalysis(id: number): Promise<AnalysisDetail> {
    const response = await this.api.get(`/api/v1/analysis/${id}`)
    return response.data
  }

  // Analisar imagem com Gemini (fallback para Hugging Face)
  async analyzeImage(id: number): Promise<AnalysisResponse> {
    const response = await this.api.post(`/api/v1/analyze/${id}`)
    return response.data
  }

  // Analisar imagem com Hugging Face
  async analyzeImageHF(id: number): Promise<AnalysisResponse> {
    const response = await this.api.post(`/api/v1/analyze-huggingface/${id}`)
    return response.data
  }

  // Obter URL da imagem
  getImageUrl(filename: string): string {
    return `${API_BASE_URL}/uploads/${filename}`
  }
}

export const apiService = new ApiService()
export default apiService
