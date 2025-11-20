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
                    {{ formatFileSize(analysis.file_size) }}
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
                  :alt="analysis.original_filename"
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
            
            <!-- Hugging Face - Linha Compacta -->
            <div class="method-row">
              <div class="method-info">
                <div class="method-icon-bg method-icon-hf">
                  <svg class="method-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="method-details">
                  <h4 class="method-title">Hugging Face</h4>
                  <p class="method-description">Análise computacional com processamento OpenCV</p>
                </div>
              </div>
              <button
                @click="analyzeImageHF"
                :disabled="loading"
                class="btn-analyze-compact btn-hf"
              >
                <svg v-if="!loading" class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <svg v-else class="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span v-if="!loading">Analisar com Hugging Face</span>
                <span v-else>Analisando com Hugging Face...</span>
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
              <span>Use ambas as IAs para uma análise mais completa e precisa</span>
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
                Selecione um método de análise acima (Gemini AI ou Hugging Face) para começar
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
  original_filename: string
  file_size: number
  upload_date: string
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

// Computed
const hasAnalysis = computed(() => {
  return analysis.value && analysis.value.results?.gemini
})

const analysisTabs = computed(() => {
  const tabs = []
  if (analysis.value?.results?.gemini) {
    tabs.push({ id: 'gemini', name: 'Gemini AI' })
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

const analyzeImageHF = async () => {
  if (!analysis.value) return
  try {
    loading.value = true
    console.log('🔄 Iniciando análise com Hugging Face...')
    
    // Usar apiService para análise com Hugging Face
    await analysisStore.analyzeImage(analysis.value.id, true)
    await loadAnalysis()
    
    console.log('✅ Análise Hugging Face concluída')
  } catch (error) {
    console.error('❌ Erro na análise com Hugging Face:', error)
    error.value = error.message || 'Erro na análise com Hugging Face'
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


const getActiveAnalysisContent = () => {
  if (activeTab.value === 'gemini' && analysis.value?.results?.gemini) {
    return marked(analysis.value.results.gemini)
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

// Lifecycle
onMounted(() => {
  loadAnalysis()
})
</script>
