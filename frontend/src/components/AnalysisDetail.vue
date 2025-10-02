<template>
  <div v-if="analysis" class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold text-gray-900">
          {{ analysis.original_filename }}
        </h2>
        <p class="text-sm text-gray-600 mt-1">
          Análise #{{ analysis.id }} • {{ formatDate(analysis.upload_date) }}
        </p>
      </div>
      
      <div class="flex items-center space-x-2">
        <span :class="getStatusBadgeClass(analysis.status)">
          {{ getStatusText(analysis.status) }}
        </span>
        
        <button
          v-if="analysis.status === 'uploaded'"
          @click="analyzeImage"
          :disabled="loading"
          class="btn-primary"
        >
          <svg v-if="loading" class="w-4 h-4 mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {{ loading ? 'Analisando com IA... (pode levar até 2 minutos)' : 'Analisar com IA' }}
        </button>
      </div>
    </div>

    <!-- Image and Analysis Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Image Section -->
      <div class="card">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Imagem Original</h3>
        
        <div class="relative">
          <img
            :src="getImageUrl(analysis.filename)"
            :alt="analysis.original_filename"
            class="w-full h-auto rounded-lg border border-gray-200"
            @error="handleImageError"
          />
          
          <!-- Image Info Overlay -->
          <div class="absolute top-2 right-2 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded">
            {{ formatFileSize(analysis.file_size) }}
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
      </div>

      <!-- Analysis Section -->
      <div class="card">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">Análise de IA</h3>
        <div v-if="analysis.status === 'processing'" class="flex items-center space-x-2 text-yellow-600">
          <svg class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <div>
            <span class="text-sm font-medium">Processando com IA...</span>
            <p class="text-xs text-gray-500">Isso pode levar até 2 minutos. Por favor, aguarde.</p>
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

        <!-- Analysis Results -->
        <div v-else-if="analysis.results.gemini" class="space-y-4">
          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex items-center justify-between mb-2">
              <h4 class="text-sm font-medium text-gray-900">Análise Técnica</h4>
              <span class="text-xs text-gray-500">Gemini AI</span>
            </div>
            
            <div class="prose prose-sm max-w-none">
              <div class="text-sm text-gray-700 whitespace-pre-wrap">
                {{ analysis.results.gemini }}
              </div>
            </div>
          </div>

          <!-- Analysis Actions -->
          <div class="flex items-center justify-between pt-4 border-t border-gray-200">
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
          @click="deleteAnalysis"
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
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysis'
import apiService from '@/services/api'

const props = defineProps<{
  analysisId: number
}>()

const router = useRouter()
const analysisStore = useAnalysisStore()

// Computed
const analysis = computed(() => analysisStore.currentAnalysis)
const loading = computed(() => analysisStore.loading)

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

function copyAnalysis() {
  if (analysis.value?.results.gemini) {
    navigator.clipboard.writeText(analysis.value.results.gemini)
    // Aqui você pode adicionar uma notificação de sucesso
    console.log('Análise copiada para a área de transferência')
  }
}

function downloadAnalysis() {
  if (analysis.value?.results.gemini) {
    const content = `Análise de Mamografia - ${analysis.value.original_filename}\n\n${analysis.value.results.gemini}`
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `analise-${analysis.value.id}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }
}

function goBack() {
  router.back()
}

function deleteAnalysis() {
  // Implementar exclusão
  console.log('Excluir análise')
}

// Lifecycle
onMounted(() => {
  loadAnalysis()
})
</script>
