<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center space-x-3">
            <button
              @click="goBack"
              class="group flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-gray-300"
            >
              <svg class="w-5 h-5 transition-transform duration-200 group-hover:-translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M15 19l-7-7 7-7" />
              </svg>
              <span class="font-medium">Voltar</span>
            </button>
            
            <div class="w-px h-6 bg-gray-300"></div>
            
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <h1 class="text-xl font-semibold text-gray-900">
                  {{ analysis?.originalFilename || 'Detalhes da Análise' }}
                </h1>
                <div class="flex items-center space-x-3 mt-1">
                  <span class="text-sm text-gray-500">Análise #{{ analysisId }}</span>
                  <span v-if="analysis" class="text-sm text-gray-500">•</span>
                  <span v-if="analysis" class="text-sm text-gray-500">{{ formatDate(analysis.uploadDate) }}</span>
                  <span v-if="analysis" :class="getStatusBadgeClass(analysis.status)" class="text-xs font-medium px-2 py-1 rounded-full">
                    {{ getStatusText(analysis.status) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Ações -->
          <div class="flex items-center space-x-3">
            <button 
              v-if="analysis"
              @click="confirmDelete" 
              class="group inline-flex items-center px-4 py-2 text-sm font-medium text-red-700 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 hover:border-red-300 hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-all duration-200 transform hover:-translate-y-0.5"
            >
              <svg class="w-4 h-4 mr-2 transition-transform duration-200 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Excluir
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Error State - ID Inválido -->
      <div v-if="!analysisId" class="text-center py-12">
        <div class="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
          <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 class="text-xl font-semibold text-gray-900 mb-2">ID de Análise Inválido</h2>
        <p class="text-gray-600 mb-6">O ID da análise não é válido ou não foi encontrado.</p>
        <button
          @click="goBack"
          class="btn-primary"
        >
          Voltar para Análises
        </button>
      </div>
      
      <!-- Analysis Detail Component -->
      <AnalysisDetail 
        v-else
        :analysis-id="analysisId.toString()" 
        @analysis-loaded="updateAnalysis" 
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import AnalysisDetail from '@/components/AnalysisDetail.vue';
import { useAnalysisStore } from '@/stores/analysis';
import { formatDate, getStatusBadgeClass, getStatusText } from '@/utils';
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps<{
  id: string
}>()

const router = useRouter()
const analysisStore = useAnalysisStore()

// State
const analysis = ref<Analysis | null>(null)

// Types
interface Analysis {
  id: number
  filename: string
  originalFilename: string
  fileSize: number
  uploadDate: string
  status: string
  geminiAnalysis?: string
  info?: {
    dimensions: [number, number]
  }
}

// Computed
const analysisId = computed(() => {
  const id = parseInt(props.id)
  if (isNaN(id) || id <= 0) {
    console.error('ID de análise inválido:', props.id)
    return null
  }
  return id
})

// Methods
function goBack() {
  router.back()
}

async function confirmDelete() {
  if (!analysis.value) return
  if (confirm('Tem certeza que deseja excluir esta análise?')) {
    try {
      await analysisStore.deleteAnalysis(analysis.value.id)
      router.push('/')
    } catch (error) {
      console.error('Erro ao excluir análise:', error)
    }
  }
}

// Expose analysis to child component
const updateAnalysis = (analysisData: Analysis) => {
  analysis.value = analysisData
}
</script>
