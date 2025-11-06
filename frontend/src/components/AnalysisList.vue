<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold
        <p class="text-sm text-gray-600 mt-1">
          {{ totalAnalyses }} análises no total
        </p>
      </div>
      
      <button
        @click="refreshAnalyses"
        :disabled="loading"
        class="btn-secondary flex items-center space-x-2"
      >
        <svg 
          :class="['w-4 h-4', { 'animate-spin': loading }]" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        <span>Atualizar</span>
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Concluídas</p>
            <p class="text-2xl font-semibold text-gray-900">{{ completedAnalyses.length }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Processando</p>
            <p class="text-2xl font-semibold text-gray-900">{{ processingAnalyses.length }}</p>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Com Erro</p>
            <p class="text-2xl font-semibold text-gray-900">{{ errorAnalyses.length }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && analyses.length === 0" class="text-center py-12">
      <div class="inline-flex items-center space-x-2 text-gray-500">
        <svg class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        <span>Carregando análises...</span>
      </div>
    </div>

    <!-- Empty State - Modernizado -->
    <div v-else-if="analyses.length === 0" class="empty-state-modern">
      <div class="empty-icon-container">
        <div class="empty-icon-bg"></div>
        <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" 
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <h3 class="empty-title">Nenhuma análise encontrada</h3>
      <p class="empty-description">Faça upload de uma imagem para começar a análise</p>
    </div>

    <!-- Analysis List - Modernizado -->
    <div v-else class="space-y-4">
      <div
        v-for="(analysis, index) in analyses"
        :key="analysis.id"
        class="analysis-card animate-fade-in"
        :style="{ animationDelay: `${index * 50}ms` }"
      >
        <!-- Status Bar colorida -->
        <div class="status-bar" :class="analysis.status"></div>
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <!-- Thumbnail -->
            <div class="flex-shrink-0">
              <img
                :src="getImageUrl(analysis.filename)"
                :alt="analysis.original_filename"
                class="w-16 h-16 object-cover rounded-lg border border-gray-200"
                @error="handleImageError"
              />
            </div>

            <!-- Info -->
            <div class="flex-1 min-w-0">
              <h3 class="text-sm font-medium text-gray-900 truncate">
                {{ analysis.original_filename }}
              </h3>
              <p class="text-xs text-gray-500 mt-1">
                {{ formatFileSize(analysis.file_size) }} • 
                {{ formatDate(analysis.upload_date) }}
              </p>
              <div class="flex items-center space-x-2 mt-2">
                <span :class="getStatusBadgeClass(analysis.status)">
                  {{ getStatusText(analysis.status) }}
                </span>
                <span v-if="analysis.has_analysis" class="text-xs text-green-600 font-medium">
                  ✓ Analisado
                </span>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center space-x-2">
            <button
              @click.stop="viewAnalysis(analysis.id)"
              class="btn-secondary btn-sm"
            >
              Ver Detalhes
            </button>
            
            <button
              v-if="analysis.status === 'uploaded'"
              @click.stop="analyzeImage(analysis.id)"
              :disabled="loading"
              class="btn-primary btn-sm"
            >
              Analisar
            </button>
            
            <button
              v-if="analysis.status === 'error'"
              @click.stop="retryAnalysis(analysis.id)"
              :disabled="loading"
              class="btn-secondary btn-sm"
            >
              Tentar Novamente
            </button>
            
            <!-- Botão de exclusão -->
            <button
              @click.stop="confirmDelete(analysis)"
              class="btn-danger btn-sm btn-icon"
              title="Excluir análise"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="analysis.status === 'error' && analysis.error_message" 
             class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-sm text-red-700">{{ analysis.error_message }}</p>
        </div>
      </div>
    </div>

    <!-- Load More Button -->
    <div v-if="analyses.length > 0" class="text-center">
      <button
        @click="loadMore"
        :disabled="loading"
        class="btn-secondary"
      >
        Carregar Mais
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import apiService from '@/services/api'
import { useAnalysisStore } from '@/stores/analysis'
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const analysisStore = useAnalysisStore()

// Computed
const analyses = computed(() => analysisStore.analyses)
const loading = computed(() => analysisStore.loading)
const totalAnalyses = computed(() => analysisStore.totalAnalyses)
const completedAnalyses = computed(() => analysisStore.completedAnalyses)
const processingAnalyses = computed(() => analysisStore.processingAnalyses)
const errorAnalyses = computed(() => analysisStore.errorAnalyses)

// Methods
async function refreshAnalyses() {
  await analysisStore.fetchAnalyses()
}

async function loadMore() {
  await analysisStore.fetchAnalyses(analyses.value.length, 10)
}

function viewAnalysis(id: number) {
  router.push(`/analysis/${id}`)
}

async function analyzeImage(id: number) {
  try {
    await analysisStore.analyzeImage(id)
  } catch (error) {
    console.error('Erro na análise:', error)
  }
}

async function retryAnalysis(id: number) {
  try {
    await analysisStore.analyzeImage(id)
  } catch (error) {
    console.error('Erro na nova tentativa:', error)
  }
}

async function confirmDelete(analysis: any) {
  const confirmed = confirm(
    `Tem certeza que deseja excluir a análise "${analysis.original_filename}"?\n\n` +
    'Esta ação não pode ser desfeita e removerá permanentemente:\n' +
    '• O arquivo da imagem\n' +
    '• Todos os dados da análise\n' +
    '• Resultados das APIs'
  )
  
  if (confirmed) {
    try {
      await analysisStore.deleteAnalysis(analysis.id)
    } catch (error) {
      console.error('Erro ao excluir análise:', error)
    }
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
  const date = new Date(dateString)
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Lifecycle
onMounted(() => {
  refreshAnalyses()
})
</script>
