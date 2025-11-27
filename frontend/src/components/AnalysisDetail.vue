<template>
  <!-- Loading State -->
  <div v-if="loading" class="text-center py-12">
    <div class="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
      <svg class="w-8 h-8 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>
    <h2 class="text-xl font-semibold text-gray-900 mb-2">Carregando Análise</h2>
    <p class="text-gray-600">Buscando detalhes da análise...</p>
  </div>

  <!-- Error State -->
  <div v-else-if="error" class="text-center py-12">
    <div class="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
      <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    </div>
    <h2 class="text-xl font-semibold text-gray-900 mb-2">Erro ao Carregar Análise</h2>
    <p class="text-gray-600 mb-6">{{ error }}</p>
    <button
      @click="loadAnalysis"
      class="btn-primary"
    >
      Tentar Novamente
    </button>
  </div>

  <!-- Analysis Content -->
  <div v-else-if="analysis">
    <!-- Conteúdo Principal -->
    <div>
      <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
        
        <!-- Coluna Esquerda: Imagem (Miniatura) - 2 colunas -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <!-- Header da Imagem -->
            <div class="px-4 py-3 border-b border-gray-200 bg-gray-50">
              <div class="flex items-center justify-between">
                <h2 class="text-sm font-semibold text-gray-900">Prévia da Imagem</h2>
                <div class="flex items-center space-x-3 text-xs text-gray-500">
                  <span class="flex items-center">
                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    {{ formatFileSize(analysis.fileSize) }}
                  </span>
                  <span class="flex items-center">
                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    {{ getImageDimensions() }}
                  </span>
                </div>
              </div>
            </div>
            
            <!-- Imagem -->
            <div class="relative bg-gray-100">
              <div class="flex items-center justify-center min-h-[200px] max-h-[300px] p-4">
                <img
                  id="analysis-thumbnail"
                  :src="getImageUrl(analysis.filename)"
                  :alt="analysis.originalFilename"
                  class="rounded-lg shadow-lg transition-transform duration-200 hover:scale-105"
                  style="max-width: 300px; max-height: 250px; width: auto; height: auto; object-fit: contain;"
                  @load="onImageLoad"
                  @error="handleImageError"
                />
              </div>
              
              <!-- Controles de Imagem -->
              <div class="absolute top-2 right-2 flex space-x-1">
                <button
                  @click="zoomIn"
                  class="group p-2 bg-white/90 hover:bg-white text-gray-600 hover:text-gray-900 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  title="Aumentar zoom"
                >
                  <svg class="w-4 h-4 transition-transform duration-200 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                  </svg>
                </button>
                <button
                  @click="zoomOut"
                  class="group p-2 bg-white/90 hover:bg-white text-gray-600 hover:text-gray-900 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  title="Diminuir zoom"
                >
                  <svg class="w-4 h-4 transition-transform duration-200 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
                  </svg>
                </button>
                <button
                  @click="rotateImage"
                  class="group p-2 bg-white/90 hover:bg-white text-gray-600 hover:text-gray-900 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  title="Rotacionar imagem"
                >
                  <svg class="w-4 h-4 transition-transform duration-200 group-hover:rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
                <button
                  @click="resetImage"
                  class="group p-2 bg-white/90 hover:bg-white text-gray-600 hover:text-gray-900 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  title="Resetar imagem"
                >
                  <svg class="w-4 h-4 transition-transform duration-200 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
              </div>
              
              <!-- Indicador de Miniatura -->
              <div class="absolute bottom-2 right-2">
                <div class="bg-gradient-to-r from-blue-600 to-blue-700 text-white text-xs px-3 py-1 rounded-full shadow-lg font-medium">
                  Miniatura
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Coluna Direita: Análise - 3 colunas -->
        <div class="lg:col-span-3">
          
          <!-- Métodos de Análise - Layout Compacto -->
          <div class="analysis-methods-compact">
            <div class="mb-4">
              <h3 class="text-lg font-semibold text-gray-900 mb-1">Análise com IA</h3>
              <p class="text-sm text-gray-600">Escolha o método de análise</p>
            </div>
            
            <!-- Gemini AI - Linha Compacta -->
            <div class="method-row">
              <div class="method-info">
                <div class="method-icon-bg">
                  <svg class="method-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                  </svg>
                </div>
                <div class="method-details">
                  <div class="method-title-row">
                    <h4 class="method-title">Gemini AI</h4>
                    <span class="method-badge">Recomendado</span>
                  </div>
                  <p class="method-description">Classificação BI-RADS e detecção de anomalias</p>
                </div>
              </div>
              <button
                @click="analyzeImage"
                :disabled="loading"
                class="btn-analyze-compact btn-gemini"
              >
                <svg v-if="!loading" class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
                <svg v-else class="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span v-if="!loading">Analisar com Gemini</span>
                <span v-else>Analisando com Gemini...</span>
              </button>
            </div>
            
            <!-- Trained Model - Linha Compacta -->
            <div class="method-row">
              <div class="method-info">
                <div class="method-icon-bg bg-green-100">
                  <svg class="method-icon text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                  </svg>
                </div>
                <div class="method-details">
                  <div class="method-title-row">
                    <h4 class="method-title">Modelo Treinado</h4>
                    <span class="method-badge bg-green-100 text-green-800">EfficientNetV2</span>
                  </div>
                  <p class="method-description">Detecção de malignidade com modelo treinado em CBIS-DDSM</p>
                </div>
              </div>
              <button
                @click="analyzeWithTrainedModel"
                :disabled="loading"
                class="btn-analyze-compact bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white"
              >
                <svg v-if="!loading" class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
                <svg v-else class="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span v-if="!loading">Analisar com Modelo</span>
                <span v-else>Analisando...</span>
              </button>
            </div>
            
            <!-- Status de Erro -->
            <div v-if="error" class="error-compact">
              <div class="error-icon">⚠️</div>
              <p class="error-text">{{ error }}</p>
              <button @click="error = null" class="error-dismiss">✕</button>
            </div>

            <!-- Dica Compacta -->
            <div v-else class="tip-compact">
              <div class="tip-icon">💡</div>
<span>Análise avançada com IA para classificação BI-RADS ou detecção de malignidade</span>
            </div>
          </div>

        </div>
      </div>

      <!-- Resultados da Análise - Largura Total -->
      <div class="mt-6">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-semibold text-gray-900">Resultados da Análise</h3>
          </div>
          
          <div class="p-6">
            <div v-if="!hasAnalysis" class="text-center py-6">
              <div class="w-12 h-12 bg-gradient-to-br from-blue-100 to-blue-50 rounded-full flex items-center justify-center mx-auto mb-4 shadow-sm empty-state-icon">
                <svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h4 class="text-xl font-semibold text-gray-800 mb-2">
                Nenhuma análise realizada
              </h4>
              <p class="text-sm text-gray-600 max-w-md mx-auto">
                Clique em "Analisar com Gemini" para iniciar a análise da imagem
              </p>
            </div>
            
            <div v-else class="space-y-6">
              <!-- Tabs de Análise -->
              <div class="border-b border-gray-200">
                <nav class="-mb-px flex space-x-1">
                  <button
                    v-for="tab in analysisTabs"
                    :key="tab.id"
                    @click="activeTab = tab.id"
                    :class="[
                      'group relative py-3 px-6 border-b-2 font-semibold text-sm transition-all duration-200 rounded-t-lg',
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600 bg-blue-50 shadow-sm'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 hover:bg-gray-50'
                    ]"
                  >
                    <span class="relative z-10">{{ tab.name }}</span>
                    <!-- Indicador ativo -->
                    <div v-if="activeTab === tab.id" class="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-8 h-0.5 bg-blue-500 rounded-full"></div>
                    <!-- Efeito de hover -->
                    <div v-if="activeTab !== tab.id" class="absolute inset-0 bg-gradient-to-r from-transparent via-gray-100 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200 rounded-t-lg"></div>
                  </button>
                </nav>
              </div>
              
              <!-- Conteúdo da Tab Ativa -->
              <div class="prose prose-sm max-w-none">
                <div v-html="getActiveAnalysisContent()"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Visualização do Diagnóstico (Modelo Treinado) -->
      <div v-if="visualizationFilename" class="mt-6">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-green-50 to-emerald-50">
            <div class="flex items-center">
              <div class="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center mr-3">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-bold text-green-900">Visualização do Diagnóstico</h3>
                <p class="text-sm text-green-700">Análise visual gerada pelo modelo treinado</p>
              </div>
            </div>
          </div>
          
          <div class="p-6 bg-gray-50">
            <div class="bg-white rounded-lg p-4 shadow-inner">
              <img
                :src="getImageUrl(visualizationFilename)"
                :alt="`Diagnóstico de ${analysis?.originalFilename}`"
                class="w-full h-auto rounded-lg shadow-lg"
                @error="handleVisualizationError"
              />
            </div>
            <div class="mt-4 text-center">
              <p class="text-sm text-gray-600 mb-3">
                <strong>Legenda:</strong> Esquerda - Imagem Original | Centro - Análise da Rede Neural | Direita - Região de Interesse
              </p>
              <a
                :href="getImageUrl(visualizationFilename)"
                :download="`diagnosis_${analysis?.originalFilename}`"
                class="inline-flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg transition-colors duration-200 shadow-sm"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Baixar Imagem de Diagnóstico
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>


<script setup lang="ts">
import apiService from '@/services/api'
import { useAnalysisStore } from '@/stores/analysis'
import { formatFileSize } from '@/utils'
import { marked } from 'marked'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

// Props
const props = defineProps<{
  analysisId: string
}>()

// Emits
const emit = defineEmits<{
  'analysis-loaded': [analysis: Analysis]
}>()

// Composables
const router = useRouter()
const analysisStore = useAnalysisStore()

// Types
interface Analysis {
  id: number
  filename: string
  originalFilename: string
  fileSize: number
  uploadDate: string
  status: string
  info?: {
    dimensions: [number, number]
  }
  results?: {
    gemini?: string
  }
}

// State
const analysis = ref<Analysis | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const activeTab = ref('gemini')
const showAnalysisOptions = ref(false)
const visualizationFilename = ref<string | null>(null)

// Computed
const hasAnalysis = computed(() => {
  return analysis.value && analysis.value.results?.gemini
})

const analysisTabs = computed(() => {
  const tabs = []
  if (analysis.value?.results?.gemini) {
    // Detectar se é do modelo treinado ou Gemini baseado no conteúdo
    const content = analysis.value.results.gemini
    const isTrainedModel = content.includes('EfficientNetV2') || content.includes('Modelo Treinado')
    
    if (isTrainedModel) {
      tabs.push({ id: 'trained', name: 'Modelo Treinado (EfficientNetV2)' })
      // Definir aba ativa automaticamente
      if (activeTab.value === 'gemini') {
        activeTab.value = 'trained'
      }
    } else {
      tabs.push({ id: 'gemini', name: 'Gemini AI' })
      // Definir aba ativa automaticamente
      if (activeTab.value !== 'gemini') {
        activeTab.value = 'gemini'
      }
    }
  }
  return tabs
})

// Methods

const analyzeImage = async () => {
  if (!analysis.value) return
  try {
    loading.value = true
    error.value = null
    console.log('🔄 Iniciando análise com Gemini...')
    
    await analysisStore.analyzeImage(analysis.value.id)
    await loadAnalysis()
    
    console.log('✅ Análise Gemini concluída')
  } catch (error) {
    console.error('❌ Erro na análise com Gemini:', error)
    error.value = error.message || 'Erro na análise com Gemini'
  } finally {
    loading.value = false
  }
}

const analyzeWithTrainedModel = async () => {
  if (!analysis.value) return
  try {
    loading.value = true
    error.value = null
    console.log('🔄 Iniciando análise com modelo treinado...')
    
    const response = await analysisStore.analyzeWithTrainedModel(analysis.value.id)
    
    // Armazenar o nome do arquivo de visualização se disponível ANTES de recarregar
    const vizFilename = response?.visualizationFilename || null
    console.log('📊 Visualization filename recebido:', vizFilename)
    
    // Recarregar análise
    await loadAnalysis()
    
    // Restaurar o filename após recarregar (pois não está no banco)
    if (vizFilename) {
      visualizationFilename.value = vizFilename
      console.log('📊 Visualization filename definido:', visualizationFilename.value)
    }
    
    console.log('✅ Análise com modelo treinado concluída')
  } catch (error) {
    console.error('❌ Erro na análise com modelo treinado:', error)
    error.value = error.message || 'Erro na análise com modelo treinado'
  } finally {
    loading.value = false
  }
}


const loadAnalysis = async () => {
  try {
    loading.value = true
    error.value = null
    console.log('🔄 Carregando análise ID:', props.analysisId)
    
    const data = await apiService.getAnalysis(parseInt(props.analysisId))
    analysis.value = data as Analysis
    emit('analysis-loaded', analysis.value)
    
    console.log('✅ Análise carregada com sucesso:', analysis.value)
  } catch (err: any) {
    console.error('❌ Erro ao carregar análise:', err)
    error.value = err.response?.data?.detail || err.message || 'Erro ao carregar análise'
  } finally {
    loading.value = false
  }
}

const getImageUrl = (filename: string) => {
  const url = apiService.getImageUrl(filename)
  console.log('🖼️ URL da imagem gerada:', { filename, url })
  return url
}

const getImageDimensions = () => {
  const dimensions = analysis.value?.info?.dimensions
  if (!dimensions || dimensions.length < 2) {
    return 'Dimensões indisponíveis'
  }

  const [widthRaw, heightRaw] = dimensions
  const width = Number(widthRaw)
  const height = Number(heightRaw)

  if (!Number.isFinite(width) || !Number.isFinite(height) || width <= 0 || height <= 0) {
    return 'Dimensões indisponíveis'
  }

  return `${width}x${height}px`
}

const generateUserFriendlyExplanation = (technicalResult: string) => {
  // Extrair informações da análise técnica
  const backgroundType = extractValue(technicalResult, /Tipo de tecido de fundo:\s*([A-Z])/i)
  const abnormalityClass = extractValue(technicalResult, /Classe de anormalidade:\s*([A-Z]+)/i)
  const severity = extractValue(technicalResult, /Severidade da anormalidade:\s*([A-Z])/i)
  
  let explanation = '<p><strong>Resumo da Análise:</strong></p><ul class="list-disc list-inside space-y-1 mt-2">'
  
  // Explicar tipo de tecido
  if (backgroundType) {
    const tissueExplanation = {
      'F': 'tecido predominantemente adiposo (menos denso)',
      'G': 'tecido fibroglandular (densidade mista)', 
      'D': 'tecido denso'
    }
    explanation += `<li><strong>Tipo de tecido:</strong> ${tissueExplanation[backgroundType] || 'não especificado'}</li>`
  }
  
  // Explicar anormalidade encontrada
  if (abnormalityClass) {
    const abnormalityExplanation = {
      'CALC': 'calcificações (depósitos de cálcio)',
      'MASS': 'massa ou nódulo',
      'ARCH': 'distorção arquitetural',
      'ASYM': 'assimetria'
    }
    explanation += `<li><strong>Achado:</strong> Foram identificadas ${abnormalityExplanation[abnormalityClass] || 'alterações'} na imagem</li>`
  }
  
  // Explicar severidade
  if (severity) {
    const severityExplanation = {
      'B': 'achado benigno (não preocupante)',
      'M': 'achado maligno (requer atenção médica)',
      'U': 'achado indeterminado (necessita avaliação adicional)'
    }
    explanation += `<li><strong>Classificação:</strong> ${severityExplanation[severity] || 'não especificada'}</li>`
  }
  
  explanation += '</ul>'
  
  // Adicionar contexto sobre BI-RADS se houver classificação
  if (severity) {
    explanation += '<p class="mt-3 text-sm"><strong>Sobre a classificação BI-RADS:</strong> '
    if (severity === 'B') {
      explanation += 'Esta classificação indica achados tipicamente benignos, que geralmente não requerem acompanhamento especial.'
    } else if (severity === 'M') {
      explanation += 'Esta classificação indica achados que podem necessitar de investigação adicional ou acompanhamento médico.'
    } else {
      explanation += 'Esta classificação requer avaliação médica para determinação da conduta apropriada.'
    }
    explanation += '</p>'
  }
  
  return explanation
}

const extractValue = (text: string, regex: RegExp): string | null => {
  const match = text.match(regex)
  return match ? match[1] : null
}


const getActiveAnalysisContent = () => {
  const content = analysis.value?.results?.gemini
  if (!content) return ''
  
  // Detectar se é do modelo treinado
  const isTrainedModel = content.includes('EfficientNetV2') || content.includes('Modelo Treinado')
  
  if (activeTab.value === 'trained' || (activeTab.value === 'gemini' && isTrainedModel)) {
    // Renderizar resultado do modelo treinado com melhor espaçamento
    const analysisHtml = marked(content)
    
    return `
      <div class="space-y-8">
        <!-- Análise do Modelo Treinado -->
        <div class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200 shadow-sm">
          <div class="flex items-center mb-4">
            <div class="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center mr-3">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
              </svg>
            </div>
            <div>
              <h4 class="text-lg font-bold text-green-900">Análise com Modelo Treinado (EfficientNetV2)</h4>
              <p class="text-sm text-green-700">Detecção de malignidade baseada em rede neural treinada</p>
            </div>
          </div>
          <div class="prose prose-green max-w-none">
            <div class="trained-model-content text-base leading-relaxed">
              ${analysisHtml}
            </div>
          </div>
        </div>

        <!-- Disclaimer Médico -->
        <div class="bg-amber-50 rounded-xl p-6 border border-amber-200 shadow-sm">
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <svg class="w-6 h-6 text-amber-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.35 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div class="ml-3">
              <h4 class="text-base font-bold text-amber-900 mb-3">⚠️ Aviso Importante</h4>
              <p class="text-sm text-amber-800 leading-relaxed mb-3">
                <strong>Esta é uma ferramenta auxiliar de análise por inteligência artificial.</strong> 
                Os resultados apresentados não substituem o diagnóstico médico profissional.
              </p>
              <p class="text-sm text-amber-800 leading-relaxed">
                É fundamental que um médico radiologista qualificado avalie as imagens e emita o laudo oficial. 
                Sempre consulte um profissional de saúde para interpretação adequada dos resultados.
              </p>
            </div>
          </div>
        </div>
      </div>
    `
  }
  
  if (activeTab.value === 'gemini' && !isTrainedModel) {
    const technicalAnalysis = marked(content)
    const userFriendlyExplanation = generateUserFriendlyExplanation(content)
    
    return `
      <div class="space-y-6">
        <!-- Análise Técnica -->
        <div class="bg-gray-50 rounded-lg p-4 border-l-4 border-blue-500">
          <h4 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Análise Técnica (Para Avaliação de Precisão)
          </h4>
          <div class="text-sm text-gray-600">
            ${technicalAnalysis}
          </div>
        </div>

        <!-- Explicação para o Usuário -->
        <div class="bg-blue-50 rounded-lg p-4 border-l-4 border-blue-600">
          <h4 class="text-sm font-semibold text-blue-800 mb-3 flex items-center">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Explicação da Análise
          </h4>
          <div class="text-sm text-blue-700">
            ${userFriendlyExplanation}
          </div>
        </div>

        <!-- Disclaimer Médico -->
        <div class="bg-amber-50 rounded-lg p-4 border-l-4 border-amber-500">
          <h4 class="text-sm font-semibold text-amber-800 mb-2 flex items-center">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.35 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            Aviso Importante
          </h4>
          <p class="text-sm text-amber-700 leading-relaxed">
            <strong>Esta é uma ferramenta auxiliar de análise por inteligência artificial.</strong> 
            Os resultados apresentados não substituem o diagnóstico médico profissional. 
            É fundamental que um médico radiologista qualificado avalie as imagens e emita o laudo oficial. 
            Sempre consulte um profissional de saúde para interpretação adequada dos resultados.
          </p>
        </div>
      </div>
    `
  }
  return '<p>Nenhuma análise disponível</p>'
}

// Image controls
const imageTransform = ref({
  scale: 1,
  rotation: 0
})

const zoomIn = () => {
  imageTransform.value.scale = Math.min(imageTransform.value.scale * 1.2, 3)
  applyImageTransform()
}

const zoomOut = () => {
  imageTransform.value.scale = Math.max(imageTransform.value.scale / 1.2, 0.5)
  applyImageTransform()
}

const rotateImage = () => {
  imageTransform.value.rotation = (imageTransform.value.rotation + 90) % 360
  applyImageTransform()
}

const resetImage = () => {
  imageTransform.value = { scale: 1, rotation: 0 }
  applyImageTransform()
}

const applyImageTransform = () => {
  const img = document.getElementById('analysis-thumbnail') as HTMLImageElement
  if (img) {
    img.style.transform = `scale(${imageTransform.value.scale}) rotate(${imageTransform.value.rotation}deg)`
  }
}

const onImageLoad = () => {
  // Callback de carregamento bem-sucedido
  console.log('Imagem carregada com sucesso')
}

const handleImageError = (event: Event) => {
  // Handler para erro de carregamento de imagem
  const img = event.target as HTMLImageElement
  console.warn('Erro ao carregar imagem:', {
    src: img.src,
    alt: img.alt
  })
  // O backend já converte PGM para JPEG automaticamente, então este erro é raro
  // Mas mantemos o handler para debug
}

const handleVisualizationError = (event: Event) => {
  // Handler para erro de carregamento da visualização
  const img = event.target as HTMLImageElement
  console.error('Erro ao carregar visualização de diagnóstico:', {
    src: img.src,
    alt: img.alt
  })
  // Tentar recarregar ou mostrar mensagem
}

// Lifecycle
onMounted(() => {
  loadAnalysis()
})
</script>

<style scoped>
/* Melhorar espaçamento do conteúdo do modelo treinado */
.trained-model-content :deep(h1) {
  @apply text-2xl font-bold text-green-900 mb-4 mt-6;
}

.trained-model-content :deep(h2) {
  @apply text-xl font-bold text-green-800 mb-3 mt-5;
}

.trained-model-content :deep(h3) {
  @apply text-lg font-semibold text-green-700 mb-3 mt-4;
}

.trained-model-content :deep(h4) {
  @apply text-base font-semibold text-green-700 mb-2 mt-3;
}

.trained-model-content :deep(p) {
  @apply mb-4 leading-relaxed text-gray-700;
}

.trained-model-content :deep(ul),
.trained-model-content :deep(ol) {
  @apply mb-4 ml-6;
}

.trained-model-content :deep(li) {
  @apply mb-2 leading-relaxed;
}

.trained-model-content :deep(strong) {
  @apply font-bold text-gray-900;
}

.trained-model-content :deep(hr) {
  @apply my-6 border-gray-300;
}

.trained-model-content :deep(blockquote) {
  @apply pl-4 border-l-4 border-green-400 italic my-4;
}

/* Espaçamento extra entre seções principais */
.trained-model-content :deep(h1:not(:first-child)),
.trained-model-content :deep(h2:not(:first-child)) {
  @apply pt-4;
}
</style>
