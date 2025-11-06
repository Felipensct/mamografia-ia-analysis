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
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <!-- Welcome Section -->
      <div class="mb-4">
        <div class="text-center">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">
            Plataforma de Análise de Mamografias com IA
          </h2>
          <p class="text-base text-gray-600 max-w-3xl mx-auto">
            Faça upload de imagens de mamografia e obtenha análises técnicas detalhadas 
            usando inteligência artificial avançada.
          </p>
        </div>
      </div>

      <!-- Stats Overview - Minimalista -->
      <div class="stats-minimal-bar mb-4">
        <div class="stat-item-minimal">
          <svg class="stat-icon-mini text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <span class="stat-label-mini">Total:</span>
          <span class="stat-value-mini text-primary-600">{{ totalAnalyses }}</span>
        </div>
        
        <div class="stat-divider"></div>
        
        <div class="stat-item-minimal">
          <svg class="stat-icon-mini text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="stat-label-mini">Concluídas:</span>
          <span class="stat-value-mini text-green-600">{{ completedAnalyses.length }}</span>
        </div>
        
        <div class="stat-divider"></div>
        
        <div class="stat-item-minimal">
          <svg class="stat-icon-mini text-orange-600 processing-indicator" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span class="stat-label-mini">Processando:</span>
          <span class="stat-value-mini text-orange-600">{{ processingAnalyses.length }}</span>
        </div>
        
        <div class="stat-divider"></div>
        
        <div class="stat-item-minimal">
          <svg class="stat-icon-mini text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="stat-label-mini">Erros:</span>
          <span class="stat-value-mini text-red-600">{{ errorAnalyses.length }}</span>
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

  </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-gray-200 mt-8">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
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
import { formatDate, getStatusDotClass, getStatusText, handleImageError } from '@/utils'
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
  if (!id || isNaN(id) || id <= 0) {
    console.error('❌ ID de análise inválido para navegação:', id)
    return
  }
  console.log('🔄 Navegando para análise ID:', id)
  router.push(`/analysis/${id}`)
}

function getImageUrl(filename: string): string {
  const url = apiService.getImageUrl(filename)
  console.log('🖼️ URL da imagem gerada:', { filename, url })
  return url
}






function scrollToUpload() {
  const uploadSection = document.querySelector('.upload-area')
  if (uploadSection) {
    uploadSection.scrollIntoView({ behavior: 'smooth' })
  }
}


// Lifecycle
onMounted(() => {
  refreshData()
})
</script>