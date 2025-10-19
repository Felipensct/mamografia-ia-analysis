<template>
  <div v-if="analysis" class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <!-- Botão de voltar -->
        <button 
          @click="goBack" 
          class="btn-back flex items-center space-x-2"
          title="Voltar"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          <span>Voltar</span>
        </button>
        
        <div>
          <h2 class="text-xl font-semibold text-gray-900">
            {{ analysis.original_filename }}
          </h2>
          <p class="text-sm text-gray-600 mt-1">
            Análise #{{ analysis.id }} • {{ formatDate(analysis.upload_date) }}
          </p>
        </div>
      </div>
      
      <div class="flex items-center space-x-3">
        <span :class="getStatusBadgeClass(analysis.status)">
          {{ getStatusText(analysis.status) }}
        </span>
        
        <!-- Botão de exclusão -->
        <button 
          @click="confirmDelete" 
          class="btn-danger btn-sm flex items-center space-x-2"
          title="Excluir análise"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          <span>Excluir</span>
        </button>
        
        <div v-if="analysis.status === 'uploaded'" class="analysis-method-selector">
          <div class="selector-header">
            <div class="icon-medical-ai">🧠</div>
            <h3 class="medical-headline">Escolha o Método de Análise</h3>
            <p class="selector-subtitle">Diferentes IAs oferecem perspectivas complementares</p>
          </div>
          
          <div class="method-cards-grid">
            <!-- Card Gemini -->
            <button
              @click="analyzeImage"
              :disabled="loading"
              class="method-card method-card-primary group"
            >
              <div class="method-badge">Recomendado</div>
              <div class="method-icon-container">
                <div class="method-icon-bg gradient-primary">
                  <span class="method-icon">🌟</span>
                </div>
              </div>
              <h4 class="method-title">Gemini AI</h4>
              <p class="method-description">Análise médica especializada e contextualizada</p>
              <ul class="method-features">
                <li>✓ BI-RADS Classification</li>
                <li>✓ Detecção de anomalias</li>
                <li>✓ Recomendações clínicas</li>
              </ul>
              <div class="method-action">
                Analisar com Gemini →
              </div>
            </button>
            
            <!-- Card Hugging Face -->
            <button
              @click="analyzeImageHF"
              :disabled="loading"
              class="method-card method-card-secondary group"
            >
              <div class="method-icon-container">
                <div class="method-icon-bg gradient-warning">
                  <span class="method-icon">🤗</span>
                </div>
              </div>
              <h4 class="method-title">Hugging Face</h4>
              <p class="method-description">Análise técnica de padrões visuais</p>
              <ul class="method-features">
                <li>✓ Análise computacional</li>
                <li>✓ Características técnicas</li>
                <li>✓ Processamento OpenCV</li>
              </ul>
              <div class="method-action">
                Analisar com HF →
              </div>
            </button>
          </div>
          
        <div class="analysis-tip">
          💡 <strong>Dica:</strong> Use ambas as APIs para uma análise mais completa
        </div>
      </div>

      </div>
    </div>

    <!-- Image and Analysis Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Image Section - Profissional -->
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Imagem Original</h3>
        
        <div class="image-viewer-professional">
          <div class="image-container-professional">
            <img
              ref="zoomableImage"
              :src="getImageUrl(analysis.filename)"
              :alt="analysis.original_filename"
              :class="['zoomable-image', { 'zoomed': isZoomed }]"
              :style="{ transform: `scale(${zoomLevel})` }"
              @click="toggleZoom"
              @error="handleImageError"
            />
            
            <!-- Controles Profissionais -->
            <div class="image-controls-professional">
              <button class="control-btn-professional" @click.stop="zoomIn" title="Ampliar">
                🔍+
                <span>Ampliar</span>
              </button>
              <button class="control-btn-professional" @click.stop="zoomOut" title="Reduzir">
                🔍-
                <span>Reduzir</span>
              </button>
              <button class="control-btn-professional" @click.stop="resetZoom" title="Resetar">
                ↻
                <span>Resetar</span>
              </button>
              <button class="control-btn-professional" @click.stop="downloadImage" title="Baixar">
                ⬇️
                <span>Baixar</span>
              </button>
            </div>
            
            <!-- Metadata Overlay -->
            <div class="image-metadata-overlay">
              <span class="metadata-badge">{{ formatFileSize(analysis.file_size) }}</span>
              <span v-if="analysis.info" class="metadata-badge">
                {{ analysis.info.dimensions[0] }}x{{ analysis.info.dimensions[1] }}px
              </span>
            </div>
            
            <!-- Resize Info Overlay -->
            <div v-if="analysis.info && analysis.info.was_resized" class="absolute bottom-2 left-2 bg-yellow-600 bg-opacity-90 text-white text-xs px-3 py-1 rounded-full">
              📏 Otimizada automaticamente
            </div>
          </div>
        </div>
        
        <!-- Image Details -->
        <div class="mt-4 grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="text-gray-500">Tamanho:</span>
            <span class="ml-2 font-medium">{{ formatFileSize(analysis.file_size) }}</span>
          </div>
          <div>
            <span class="text-gray-500">Enviado em:</span>
            <span class="ml-2 font-medium">{{ formatDate(analysis.upload_date) }}</span>
          </div>
        </div>
        
        <!-- Resize Information (se foi redimensionada) -->
        <div v-if="analysis.info && analysis.info.was_resized" class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div class="flex items-center space-x-2 text-yellow-800">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="font-medium text-sm">Imagem Otimizada Automaticamente</span>
          </div>
          <div class="mt-2 text-sm text-yellow-700">
            <p><strong>Dimensões originais:</strong> {{ analysis.info.original_dimensions?.[0] }}x{{ analysis.info.original_dimensions?.[1] }}px</p>
            <p><strong>Dimensões atuais:</strong> {{ analysis.info.dimensions[0] }}x{{ analysis.info.dimensions[1] }}px</p>
            <p class="mt-1 text-xs">A imagem foi redimensionada automaticamente para otimizar a análise de IA, mantendo a qualidade e proporção originais.</p>
          </div>
        </div>
      </div>

      <!-- Analysis Section - Modernizada com Tabs -->
      <div class="card">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">Análise de IA</h3>
        </div>
        
        <!-- Tabs de Análise -->
        <div v-if="hasGeminiAnalysis || hasHFAnalysis" class="analysis-tabs">
          <button
            v-if="hasGeminiAnalysis"
            :class="['tab-btn', { active: activeTab === 'gemini' }]"
            @click="activeTab = 'gemini'"
          >
            <span>🌟</span>
            <span>Gemini AI</span>
          </button>
          <button
            v-if="hasHFAnalysis"
            :class="['tab-btn', { active: activeTab === 'hf' }]"
            @click="activeTab = 'hf'"
          >
            <span>🤗</span>
            <span>Hugging Face</span>
          </button>
          <button
            :class="['tab-btn', { active: activeTab === 'metadata' }]"
            @click="activeTab = 'metadata'"
          >
            <span>📊</span>
            <span>Metadados</span>
          </button>
        </div>
        
        <!-- Processing State with Progress -->
        <div v-if="analysis.status === 'processing'" class="space-y-4">
          <div class="flex items-center space-x-2 text-yellow-600">
            <svg class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <div>
              <span class="text-sm font-medium">Processando com IA...</span>
              <p class="text-xs text-gray-500">Isso pode levar até 2 minutos. Por favor, aguarde.</p>
            </div>
          </div>
          
          <!-- Progress Bar -->
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div class="bg-yellow-500 h-2 rounded-full animate-pulse" style="width: 100%"></div>
          </div>
          
          <!-- Processing Steps -->
          <div class="space-y-2 text-sm">
            <div class="flex items-center space-x-2 text-gray-600">
              <div class="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>Imagem carregada e validada</span>
            </div>
            <div class="flex items-center space-x-2 text-gray-600">
              <div class="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
              <span>Enviando para análise de IA...</span>
            </div>
            <div class="flex items-center space-x-2 text-gray-400">
              <div class="w-2 h-2 bg-gray-300 rounded-full"></div>
              <span>Processando resultados</span>
            </div>
          </div>
        </div>

        <!-- No Analysis State -->
        <div v-if="!analysis.results.gemini && analysis.status !== 'processing'" 
             class="text-center py-8">
          <div class="mx-auto w-16 h-16 text-gray-300 mb-4">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" 
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h4 class="text-lg font-medium text-gray-900 mb-2">Nenhuma análise disponível</h4>
          <p class="text-gray-600 mb-4">Execute uma análise para ver os resultados</p>
          <button
            @click="analyzeImage"
            :disabled="loading"
            class="btn-primary"
          >
            Iniciar Análise
          </button>
        </div>

        <!-- Analysis Results - Com Tabs -->
        <div v-else-if="hasGeminiAnalysis || hasHFAnalysis" class="tab-content">
          <!-- Tab Panel: Gemini -->
          <div v-if="activeTab === 'gemini' && hasGeminiAnalysis" class="tab-panel">
            <div class="bg-gray-50 rounded-lg p-4">
              <div class="flex items-center justify-between mb-3">
                <h4 class="text-sm font-medium text-gray-900">Análise Médica Especializada</h4>
                <span class="badge-with-dot">
                  <span class="badge-dot success"></span>
                  <span class="text-xs text-gray-600">Gemini AI</span>
                </span>
              </div>
              
              <div class="markdown-content prose prose-sm max-w-none">
                <div v-html="renderMarkdown(analysis.results.gemini || '')"></div>
              </div>
            </div>
          </div>
          
          <!-- Tab Panel: Hugging Face -->
          <div v-if="activeTab === 'hf' && hasHFAnalysis" class="tab-panel">
            <div class="bg-gray-50 rounded-lg p-4">
              <div class="flex items-center justify-between mb-3">
                <h4 class="text-sm font-medium text-gray-900">Análise Computacional</h4>
                <span class="badge-with-dot">
                  <span class="badge-dot warning"></span>
                  <span class="text-xs text-gray-600">Hugging Face / OpenCV</span>
                </span>
              </div>
              
              <div class="markdown-content prose prose-sm max-w-none">
                <div v-html="renderMarkdown(analysis.results.gpt4v || '')"></div>
              </div>
            </div>
          </div>
          
          <!-- Tab Panel: Metadados -->
          <div v-if="activeTab === 'metadata'" class="tab-panel">
            <div class="glass-card p-4">
              <h4 class="text-sm font-medium text-gray-900 mb-4">Informações Técnicas</h4>
              
              <div class="space-y-3">
                <div class="meta-item">
                  <span class="meta-label">ID da Análise</span>
                  <span class="meta-value">#{{ analysis.id }}</span>
                </div>
                
                <div class="meta-item">
                  <span class="meta-label">Nome do Arquivo</span>
                  <span class="meta-value">{{ analysis.original_filename }}</span>
                </div>
                
                <div class="meta-item">
                  <span class="meta-label">Tamanho</span>
                  <span class="meta-value">{{ formatFileSize(analysis.file_size) }}</span>
                </div>
                
                <div class="meta-item">
                  <span class="meta-label">Upload</span>
                  <span class="meta-value">{{ formatDate(analysis.upload_date) }}</span>
                </div>
                
                <div v-if="analysis.processing_date" class="meta-item">
                  <span class="meta-label">Processamento</span>
                  <span class="meta-value">{{ formatDate(analysis.processing_date) }}</span>
                </div>
                
                <div v-if="analysis.info" class="meta-item">
                  <span class="meta-label">Dimensões</span>
                  <span class="meta-value">
                    {{ analysis.info.dimensions[0] }} x {{ analysis.info.dimensions[1] }}px
                  </span>
                </div>
                
                <div v-if="analysis.info?.original_dimensions" class="meta-item">
                  <span class="meta-label">Dimensões Originais</span>
                  <span class="meta-value">
                    {{ analysis.info?.original_dimensions?.[0] }} x {{ analysis.info?.original_dimensions?.[1] }}px
                  </span>
                </div>
                
                <div v-if="analysis.info" class="meta-item">
                  <span class="meta-label">Formato</span>
                  <span class="meta-value">{{ analysis.info.format }}</span>
                </div>
                
                <div v-if="analysis.info" class="meta-item">
                  <span class="meta-label">Modo de Cor</span>
                  <span class="meta-value">{{ analysis.info.mode }}</span>
                </div>
                
                <div v-if="analysis.info" class="meta-item">
                  <span class="meta-label">Otimizada</span>
                  <span class="meta-value">{{ analysis.info.is_optimized ? '✅ Sim' : '❌ Não' }}</span>
                </div>
                
                <div v-if="analysis.info" class="meta-item">
                  <span class="meta-label">Redimensionada</span>
                  <span class="meta-value">{{ analysis.info.was_resized ? '✅ Sim' : '❌ Não' }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Analysis Actions -->
          <div v-if="hasGeminiAnalysis || hasHFAnalysis" class="flex items-center justify-between pt-4 mt-4 border-t border-gray-200">
            <div class="flex items-center space-x-2 text-sm text-gray-500">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Processado em {{ formatDate(analysis.processing_date || '') }}</span>
            </div>
            
            <div class="flex items-center space-x-2">
              <button
                @click="copyAnalysis"
                class="text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                Copiar Análise
              </button>
              <button
                @click="downloadAnalysis"
                class="text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                Baixar PDF
              </button>
            </div>
          </div>
        </div>

        <!-- Error State -->
        <div v-else-if="analysis.status === 'error'" class="text-center py-8">
          <div class="mx-auto w-16 h-16 text-red-300 mb-4">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" 
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h4 class="text-lg font-medium text-gray-900 mb-2">Erro na Análise</h4>
          <p class="text-gray-600 mb-4">{{ analysis.error_message || 'Ocorreu um erro durante a análise' }}</p>
          <button
            @click="retryAnalysis"
            :disabled="loading"
            class="btn-primary"
          >
            Tentar Novamente
          </button>
        </div>
      </div>
    </div>

    <!-- Additional Actions -->
    <div class="flex items-center justify-between pt-6 border-t border-gray-200">
      <button
        @click="goBack"
        class="btn-secondary flex items-center space-x-2"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M15 19l-7-7 7-7" />
        </svg>
        <span>Voltar</span>
      </button>
      
      <div class="flex items-center space-x-2">
        <button
          @click="confirmDelete"
          class="btn-danger"
        >
          Excluir Análise
        </button>
      </div>
    </div>
  </div>

  <!-- Loading State -->
  <div v-else-if="loading" class="text-center py-12">
    <div class="inline-flex items-center space-x-2 text-gray-500">
      <svg class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
      <span>Carregando análise...</span>
    </div>
  </div>

  <!-- Not Found State -->
  <div v-else class="text-center py-12">
    <div class="mx-auto w-24 h-24 text-gray-300 mb-4">
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" 
              d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    </div>
    <h3 class="text-lg font-medium text-gray-900 mb-2">Análise não encontrada</h3>
    <p class="text-gray-600 mb-4">A análise solicitada não foi encontrada</p>
    <button @click="goBack" class="btn-primary">
      Voltar para Lista
    </button>
  </div>
</template>

<script setup lang="ts">
import { useToast } from '@/composables/useToast'
import apiService from '@/services/api'
import { useAnalysisStore } from '@/stores/analysis'
import { marked } from 'marked'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps<{
  analysisId: number
}>()

const router = useRouter()
const analysisStore = useAnalysisStore()
const { success } = useToast()

// Refs para Image Viewer
const zoomableImage = ref<HTMLImageElement>()
const zoomLevel = ref(1)
const isZoomed = ref(false)
const activeTab = ref<'gemini' | 'hf' | 'metadata' | 'compare'>('gemini')

// Computed
const analysis = computed(() => analysisStore.currentAnalysis)
const loading = computed(() => analysisStore.loading)
const hasGeminiAnalysis = computed(() => {
  return analysis.value?.results?.gemini && analysis.value.results.gemini.trim() !== ''
})
const hasHFAnalysis = computed(() => {
  return analysis.value?.results?.gpt4v && analysis.value.results.gpt4v.trim() !== ''
})

// Methods
async function loadAnalysis() {
  await analysisStore.fetchAnalysis(props.analysisId)
}

async function analyzeImage() {
  try {
    await analysisStore.analyzeImage(props.analysisId)
  } catch (error) {
    console.error('Erro na análise:', error)
  }
}

async function analyzeImageHF() {
  try {
    await analysisStore.analyzeImage(props.analysisId, true) // true = use HuggingFace
  } catch (error) {
    console.error('Erro na análise com HuggingFace:', error)
  }
}

async function retryAnalysis() {
  try {
    await analysisStore.analyzeImage(props.analysisId)
  } catch (error) {
    console.error('Erro na nova tentativa:', error)
  }
}

function getImageUrl(filename: string): string {
  return apiService.getImageUrl(filename)
}

function handleImageError(event: Event) {
  const img = event.target as HTMLImageElement
  img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCA2NCA2NCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjY0IiBoZWlnaHQ9IjY0IiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0yNCAyNEg0MFY0MEgyNFYyNFoiIGZpbGw9IiNEMUQ1REIiLz4KPC9zdmc+'
}

function getStatusBadgeClass(status: string): string {
  const classes = {
    uploaded: 'status-badge status-uploaded',
    processing: 'status-badge status-processing',
    completed: 'status-badge status-completed',
    error: 'status-badge status-error'
  }
  return classes[status as keyof typeof classes] || 'status-badge status-uploaded'
}

function getStatusText(status: string): string {
  const texts = {
    uploaded: 'Enviado',
    processing: 'Processando',
    completed: 'Concluído',
    error: 'Erro'
  }
  return texts[status as keyof typeof texts] || status
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

function formatDate(dateString: string): string {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function goBack() {
  router.back()
}

async function confirmDelete() {
  if (!analysis.value) return
  
  const confirmed = confirm(
    `Tem certeza que deseja excluir a análise "${analysis.value.original_filename}"?\n\n` +
    'Esta ação não pode ser desfeita e removerá permanentemente:\n' +
    '• O arquivo da imagem\n' +
    '• Todos os dados da análise\n' +
    '• Resultados das APIs'
  )
  
  if (confirmed) {
    try {
      await analysisStore.deleteAnalysis(props.analysisId)
      router.push('/analyses')
    } catch (error) {
      console.error('Erro ao excluir análise:', error)
    }
  }
}

function copyAnalysis() {
  let textToCopy = ''
  
  if (activeTab.value === 'gemini' && analysis.value?.results.gemini) {
    textToCopy = analysis.value.results.gemini
  } else if (activeTab.value === 'hf' && analysis.value?.results.gpt4v) {
    textToCopy = analysis.value.results.gpt4v
  } else if (activeTab.value === 'metadata' && analysis.value) {
    textToCopy = `Metadados - Análise #${analysis.value.id}\n` +
                 `Arquivo: ${analysis.value.original_filename}\n` +
                 `Tamanho: ${formatFileSize(analysis.value.file_size)}\n` +
                 `Upload: ${formatDate(analysis.value.upload_date)}`
  }
  
  if (textToCopy) {
    navigator.clipboard.writeText(textToCopy)
    success('Copiado!', 'Conteúdo copiado para a área de transferência')
  }
}

function downloadAnalysis() {
  let content = ''
  let filename = `analise-${analysis.value?.id}`
  
  if (activeTab.value === 'gemini' && analysis.value?.results.gemini) {
    content = `Análise de Mamografia - ${analysis.value.original_filename}\n\nGemini AI\n${'='.repeat(50)}\n\n${analysis.value.results.gemini}`
    filename += '-gemini.txt'
  } else if (activeTab.value === 'hf' && analysis.value?.results.gpt4v) {
    content = `Análise de Mamografia - ${analysis.value.original_filename}\n\nHugging Face\n${'='.repeat(50)}\n\n${analysis.value.results.gpt4v}`
    filename += '-hf.txt'
  } else if (analysis.value?.results.gemini) {
    content = `Análise de Mamografia - ${analysis.value.original_filename}\n\n${analysis.value.results.gemini}`
    filename += '.txt'
  }
  
  if (content) {
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }
}

// Image Viewer Functions
function zoomIn() {
  if (zoomLevel.value < 3) {
    zoomLevel.value += 0.25
    isZoomed.value = true
  }
}

function zoomOut() {
  if (zoomLevel.value > 1) {
    zoomLevel.value -= 0.25
    if (zoomLevel.value <= 1) {
      zoomLevel.value = 1
      isZoomed.value = false
    }
  }
}

function resetZoom() {
  zoomLevel.value = 1
  isZoomed.value = false
}

function toggleZoom() {
  if (isZoomed.value) {
    resetZoom()
  } else {
    zoomLevel.value = 2
    isZoomed.value = true
  }
}

function downloadImage() {
  if (analysis.value?.filename) {
    const link = document.createElement('a')
    link.href = getImageUrl(analysis.value.filename)
    link.download = analysis.value.original_filename || 'mamografia.jpg'
    link.click()
  }
}

function renderMarkdown(text: string): string {
  try {
    return marked(text) as string
  } catch (error) {
    console.error('Erro ao renderizar markdown:', error)
    return text
  }
}

const copyResult = async (type: string) => {
  try {
    if (!analysis.value) return
    
    const text = type === 'gemini' 
      ? analysis.value.results.gemini 
      : analysis.value.results.gpt4v
    
    if (text) {
      await navigator.clipboard.writeText(text)
      success('Resultado copiado para a área de transferência!', 'success')
    }
  } catch (error) {
    console.error('Erro ao copiar:', error)
  }
}

const downloadResult = (type: string) => {
  if (!analysis.value) return
  
  const text = type === 'gemini' 
    ? analysis.value.results.gemini 
    : analysis.value.results.gpt4v
  
  if (!text) return
  
  const filename = `${analysis.value.original_filename || 'mamografia'}_${type}_analysis.txt`
  
  const blob = new Blob([text], { type: 'text/plain' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = filename
  link.click()
  
  success(`Relatório ${type} baixado com sucesso!`, 'success')
}

// Lifecycle
onMounted(() => {
  loadAnalysis()
})
</script>
