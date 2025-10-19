<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h1 class="text-xl font-semibold text-gray-900">Mamografia IA</h1>
              <p class="text-xs text-gray-500">Análise Inteligente de Imagens</p>
            </div>
          </div>
          
          <div class="flex items-center space-x-4">
            <button
              @click="refreshData"
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
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Welcome Section -->
      <div class="mb-8">
        <div class="text-center">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">
            Plataforma de Análise de Mamografias com IA
          </h2>
          <p class="text-lg text-gray-600 max-w-3xl mx-auto">
            Faça upload de imagens de mamografia e obtenha análises técnicas detalhadas 
            usando inteligência artificial avançada.
          </p>
        </div>
      </div>

      <!-- Stats Overview - Profissional -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8 animate-fade-in">
        <div class="stat-card-modern">
          <div class="stat-icon-container">
            <div class="stat-icon-bg">
              <svg class="stat-icon-large" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
          </div>
          <p class="stat-label">Total de Análises</p>
          <p class="stat-value">{{ totalAnalyses }}</p>
          <div class="stat-trend">
            <span class="trend-up">↑ 12%</span>
            <span class="trend-label">vs. semana anterior</span>
          </div>
        </div>

        <div class="stat-card-modern">
          <div class="stat-icon-container">
            <div class="stat-icon-bg" style="background: var(--gradient-success);">
              <svg class="stat-icon-large" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <p class="stat-label">Concluídas</p>
          <p class="stat-value" style="background: var(--gradient-success); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{{ completedAnalyses.length }}</p>
          <div class="stat-trend">
            <span class="trend-up">↑ 8%</span>
            <span class="trend-label">taxa de sucesso</span>
          </div>
        </div>

        <div class="stat-card-modern">
          <div class="stat-icon-container">
            <div class="stat-icon-bg" style="background: var(--gradient-warning);">
              <svg class="stat-icon-large processing-indicator" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </div>
          </div>
          <p class="stat-label">Processando</p>
          <p class="stat-value" style="background: var(--gradient-warning); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{{ processingAnalyses.length }}</p>
          <div class="stat-trend">
            <span class="trend-label">em andamento</span>
          </div>
        </div>

        <div class="stat-card-modern">
          <div class="stat-icon-container">
            <div class="stat-icon-bg" style="background: var(--gradient-danger);">
              <svg class="stat-icon-large" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <p class="stat-label">Com Erro</p>
          <p class="stat-value" style="background: var(--gradient-danger); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{{ errorAnalyses.length }}</p>
          <div class="stat-trend">
            <span class="trend-down">↓ 5%</span>
            <span class="trend-label">taxa de erro</span>
          </div>
        </div>
      </div>

      <!-- Main Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Upload Section -->
        <div>
          <ImageUpload />
        </div>

        <!-- Recent Analyses -->
        <div>
          <div class="card">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-lg font-semibold text-gray-900">Análises Recentes</h3>
              <button
                @click="viewAllAnalyses"
                class="text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                Ver todas
              </button>
            </div>

            <!-- Recent Analyses List - Profissional -->
            <div v-if="recentAnalyses.length > 0" class="space-y-3">
              <div
                v-for="(analysis, index) in recentAnalyses"
                :key="analysis.id"
                @click="viewAnalysis(analysis.id)"
                class="recent-analysis-item"
                :style="{ animationDelay: `${index * 50}ms` }"
              >
                <img
                  :src="getImageUrl(analysis.filename)"
                  :alt="analysis.original_filename"
                  class="recent-analysis-thumbnail"
                  @error="handleImageError"
                />
                <div class="recent-analysis-info">
                  <p class="recent-analysis-title">
                    {{ analysis.original_filename }}
                  </p>
                  <p class="recent-analysis-date">
                    {{ formatDate(analysis.upload_date) }}
                  </p>
                </div>
                <span class="badge-with-dot">
                  <span 
                    class="dot-pulse" 
                    :class="getStatusDotClass(analysis.status)"
                  ></span>
                  {{ getStatusText(analysis.status) }}
                </span>
              </div>
            </div>

            <!-- Empty State - Profissional -->
            <div v-else class="empty-state-professional">
              <div class="empty-icon-glow">
                <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" 
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 class="empty-title">Nenhuma análise recente</h3>
              <p class="empty-description">Faça upload da primeira mamografia para começar a análise com IA</p>
              <button class="btn-cta" @click="scrollToUpload">
                <span>📁</span>
                <span>Começar Agora</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Features Section -->
      <div class="mt-12">
        <div class="text-center mb-8">
          <h3 class="text-2xl font-bold text-gray-900 mb-4">Recursos da Plataforma</h3>
          <p class="text-gray-600 max-w-2xl mx-auto">
            Tecnologia avançada para análise técnica de imagens de mamografia
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="card text-center">
            <div class="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h4 class="text-lg font-semibold text-gray-900 mb-2">IA Avançada</h4>
            <p class="text-sm text-gray-600">
              Análise com Gemini AI e Hugging Face para resultados precisos
            </p>
          </div>

          <div class="card text-center">
            <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h4 class="text-lg font-semibold text-gray-900 mb-2">Processamento Rápido</h4>
            <p class="text-sm text-gray-600">
              Análise em segundos com processamento otimizado
            </p>
          </div>

          <div class="card text-center">
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h4 class="text-lg font-semibold text-gray-900 mb-2">Seguro e Confiável</h4>
            <p class="text-sm text-gray-600">
              Dados protegidos com criptografia e privacidade garantida
            </p>
          </div>
        </div>
      </div>
  </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-gray-200 mt-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="text-center text-sm text-gray-500">
          <p>&copy; 2024 Mamografia IA. Plataforma de análise inteligente de imagens médicas.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import ImageUpload from '@/components/ImageUpload.vue'
import apiService from '@/services/api'
import { useAnalysisStore } from '@/stores/analysis'
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const analysisStore = useAnalysisStore()

// Computed
const loading = computed(() => analysisStore.loading)
const totalAnalyses = computed(() => analysisStore.totalAnalyses)
const completedAnalyses = computed(() => analysisStore.completedAnalyses)
const processingAnalyses = computed(() => analysisStore.processingAnalyses)
const errorAnalyses = computed(() => analysisStore.errorAnalyses)

const recentAnalyses = computed(() => 
  analysisStore.analyses.slice(0, 5) // Mostrar apenas as 5 mais recentes
)

// Methods
async function refreshData() {
  await analysisStore.fetchAnalyses()
}

function viewAllAnalyses() {
  router.push('/analyses')
}

function viewAnalysis(id: number) {
  router.push(`/analysis/${id}`)
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

function getStatusGradient(status: string): string {
  const gradients = {
    uploaded: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
    processing: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    completed: 'linear-gradient(135deg, #16a34a 0%, #15803d 100%)',
    error: 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)'
  }
  return gradients[status as keyof typeof gradients] || gradients.uploaded
}

function getStatusDotClass(status: string): string {
  const dotClasses = {
    uploaded: 'dot-primary',
    processing: 'dot-warning',
    completed: 'dot-success',
    error: 'dot-danger'
  }
  return dotClasses[status as keyof typeof dotClasses] || 'dot-primary'
}

function scrollToUpload() {
  const uploadSection = document.querySelector('.upload-area')
  if (uploadSection) {
    uploadSection.scrollIntoView({ behavior: 'smooth' })
  }
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
  refreshData()
})
</script>