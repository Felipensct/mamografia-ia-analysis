import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Analysis, AnalysisDetail, UploadResponse, AnalysisResponse } from '@/services/api'
import apiService from '@/services/api'

export const useAnalysisStore = defineStore('analysis', () => {
  // Estado
  const analyses = ref<Analysis[]>([])
  const currentAnalysis = ref<AnalysisDetail | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const uploadProgress = ref(0)

  // Getters computados
  const completedAnalyses = computed(() => 
    analyses.value.filter(a => a.status === 'completed')
  )
  
  const processingAnalyses = computed(() => 
    analyses.value.filter(a => a.status === 'processing')
  )
  
  const errorAnalyses = computed(() => 
    analyses.value.filter(a => a.status === 'error')
  )

  const totalAnalyses = computed(() => analyses.value.length)

  // Actions
  async function fetchAnalyses(skip = 0, limit = 10) {
    try {
      loading.value = true
      error.value = null
      
      const response = await apiService.getAnalyses(skip, limit)
      analyses.value = response.analyses
      
      return response
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Erro ao carregar análises'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchAnalysis(id: number) {
    try {
      loading.value = true
      error.value = null
      
      const analysis = await apiService.getAnalysis(id)
      currentAnalysis.value = analysis
      
      // Atualizar na lista se existir
      const index = analyses.value.findIndex(a => a.id === id)
      if (index !== -1) {
        analyses.value[index] = { ...analyses.value[index], ...analysis }
      }
      
      return analysis
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Erro ao carregar análise'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function uploadImage(file: File): Promise<UploadResponse> {
    try {
      console.log('🔄 Store: Iniciando upload da imagem:', file.name)
      loading.value = true
      error.value = null
      uploadProgress.value = 0
      
      // Simular progresso de upload
      const progressInterval = setInterval(() => {
        if (uploadProgress.value < 90) {
          uploadProgress.value += Math.random() * 10
        }
      }, 100)
      
      console.log('🔄 Store: Chamando apiService.uploadImage...')
      const response = await apiService.uploadImage(file)
      console.log('✅ Store: Upload concluído com sucesso:', response)
      
      clearInterval(progressInterval)
      uploadProgress.value = 100
      
      // Adicionar à lista de análises
      const newAnalysis: Analysis = {
        id: response.analysis_id,
        filename: response.filename,
        original_filename: response.original_filename,
        file_size: response.file_size,
        upload_date: new Date().toISOString(),
        status: 'uploaded',
        is_processed: false,
        has_analysis: false,
      }
      
      analyses.value.unshift(newAnalysis)
      
      return response
    } catch (err: any) {
      console.error('❌ Store: Erro no upload:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        stack: err.stack
      })
      error.value = err.response?.data?.detail || err.message || 'Erro no upload'
      throw err
    } finally {
      loading.value = false
      uploadProgress.value = 0
    }
  }

  async function analyzeImage(id: number, useHuggingFace = false): Promise<AnalysisResponse> {
    try {
      loading.value = true
      error.value = null
      
      // Atualizar status para processando
      const analysis = analyses.value.find(a => a.id === id)
      if (analysis) {
        analysis.status = 'processing' as const
      }
      
      const response = useHuggingFace 
        ? await apiService.analyzeImageHF(id)
        : await apiService.analyzeImage(id)
      
      // Atualizar status na lista
      if (analysis) {
        analysis.status = response.status as 'uploaded' | 'processing' | 'completed' | 'error'
        analysis.is_processed = response.status === 'completed'
        analysis.has_analysis = !!response.analysis
        analysis.processing_date = new Date().toISOString()
      }
      
      // Atualizar análise atual se for a mesma
      if (currentAnalysis.value?.id === id) {
        currentAnalysis.value.status = response.status as 'uploaded' | 'processing' | 'completed' | 'error'
        currentAnalysis.value.is_processed = response.status === 'completed'
        if (response.analysis) {
          currentAnalysis.value.results.gemini = response.analysis
        }
      }
      
      return response
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Erro na análise'
      
      // Atualizar status para erro
      const analysis = analyses.value.find(a => a.id === id)
      if (analysis) {
        analysis.status = 'error' as const
        analysis.error_message = error.value || undefined
      }
      
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  function clearCurrentAnalysis() {
    currentAnalysis.value = null
  }

  return {
    // Estado
    analyses,
    currentAnalysis,
    loading,
    error,
    uploadProgress,
    
    // Getters
    completedAnalyses,
    processingAnalyses,
    errorAnalyses,
    totalAnalyses,
    
    // Actions
    fetchAnalyses,
    fetchAnalysis,
    uploadImage,
    analyzeImage,
    clearError,
    clearCurrentAnalysis,
  }
})
