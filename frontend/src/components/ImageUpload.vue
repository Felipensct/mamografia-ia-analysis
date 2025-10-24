<template>
  <div class="card">
    <div class="text-center mb-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-2">
        Upload de Imagem de Mamografia
      </h3>
      <p class="text-sm text-gray-600">
        Faça upload de uma imagem para análise com IA
      </p>
    </div>

    <!-- Área de Upload - Modernizada -->
    <div
      ref="dropZone"
      :class="[
        'upload-area',
        'glass-effect',
        'transition-all',
        { 'dragover': isDragOver },
        { 'opacity-50': loading },
        { 'scale-in': !loading }
      ]"
      @click="triggerFileInput"
      @dragover.prevent="handleDragOver"
      @dragleave.prevent="handleDragLeave"
      @drop.prevent="handleDrop"
    >
      <input
        ref="fileInput"
        type="file"
        accept="image/*,.dcm"
        @change="handleFileSelect"
        class="hidden"
        :disabled="loading"
      />

      <div v-if="!loading" class="space-y-4">
        <div class="mx-auto w-12 h-12 text-gray-400">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </div>
        
        <div>
          <p class="text-lg font-medium text-gray-900">
            {{ isDragOver ? 'Solte a imagem aqui' : 'Clique ou arraste uma imagem' }}
          </p>
          <p class="text-sm text-gray-500 mt-1">
            Formatos suportados: PNG, JPG, JPEG, TIFF, BMP, DICOM (.dcm)
          </p>
          <p class="text-xs text-gray-400 mt-1">
            Tamanho máximo: 10MB (imagens) / 50MB (DICOM)
          </p>
        </div>
      </div>

      <!-- Loading State -->
      <div v-else class="space-y-4">
        <div class="mx-auto w-12 h-12 text-primary-600 animate-spin">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </div>
        
        <div>
          <p class="text-lg font-medium text-gray-900">
            Enviando imagem...
          </p>
          <p class="text-sm text-gray-500 mt-1">
            {{ uploadProgress }}% concluído
          </p>
        </div>

        <!-- Progress Bar -->
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div 
            class="bg-primary-600 h-2 rounded-full transition-all duration-300"
            :style="{ width: `${uploadProgress}%` }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Preview da Imagem Selecionada -->
    <div v-if="selectedFile && !loading" class="mt-6">
      <div class="flex items-center justify-between mb-3">
        <h4 class="text-sm font-medium text-gray-900">Imagem Selecionada</h4>
        <button
          @click="clearFile"
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <div class="border border-gray-200 rounded-lg p-4">
        <div class="flex items-center space-x-4">
          <img
            :src="imagePreview"
            :alt="selectedFile.name"
            class="w-16 h-16 object-cover rounded-lg"
          />
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-gray-900 truncate">
              {{ selectedFile.name }}
            </p>
            <p class="text-xs text-gray-500">
              {{ formatFileSize(selectedFile.size) }}
            </p>
            <div class="mt-1 text-xs text-blue-600">
              💡 Imagens grandes serão redimensionadas automaticamente
            </div>
            <p class="text-xs text-gray-400">
              {{ imageDimensions }}
            </p>
          </div>
          <button
            @click="uploadFile"
            class="btn-primary"
            :disabled="loading"
          >
            Enviar
          </button>
        </div>
      </div>
    </div>

    <!-- Mensagem de Erro -->
    <div v-if="error" class="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">Erro no Upload</h3>
          <p class="text-sm text-red-700 mt-1">{{ error }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAnalysisStore } from '@/stores/analysis'
import { computed, ref } from 'vue'
import { formatFileSize, isValidImageFile, isValidFileSize, createImagePreview } from '@/utils'

const analysisStore = useAnalysisStore()

// Refs
const fileInput = ref<HTMLInputElement>()
const dropZone = ref<HTMLDivElement>()
const selectedFile = ref<File | null>(null)
const isDragOver = ref(false)

// Computed
const loading = computed(() => analysisStore.uploadLoading)
const uploadProgress = computed(() => analysisStore.uploadProgress)
const error = computed(() => analysisStore.error)

const imagePreview = computed(() => {
  if (!selectedFile.value) return ''
  return createImagePreview(selectedFile.value)
})

const imageDimensions = computed(() => {
  if (!selectedFile.value) return ''
  // Simular dimensões (em um caso real, você carregaria a imagem para obter as dimensões reais)
  return 'Dimensões serão calculadas após upload'
})

// Methods
function triggerFileInput() {
  if (!loading.value) {
    fileInput.value?.click()
  }
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    selectFile(file)
  }
}

function handleDragOver(event: DragEvent) {
  event.preventDefault()
  isDragOver.value = true
}

function handleDragLeave(event: DragEvent) {
  event.preventDefault()
  isDragOver.value = false
}

function handleDrop(event: DragEvent) {
  event.preventDefault()
  isDragOver.value = false
  
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    const file = files[0]
    if (file) {
      selectFile(file)
    }
  }
}

function selectFile(file: File) {
  // Limpar erros anteriores
  analysisStore.clearError()
  
  // Validar tipo de arquivo
  if (!isValidImageFile(file)) {
    analysisStore.error = 'Tipo de arquivo não suportado. Use PNG, JPG, JPEG, TIFF, BMP ou DICOM (.dcm)'
    return
  }

  // Validar tamanho do arquivo
  if (!isValidFileSize(file)) {
    const isDicom = file.name.toLowerCase().endsWith('.dcm') || file.type === 'application/dicom'
    const maxSize = isDicom ? 50 : 10
    const maxSizeBytes = maxSize * 1024 * 1024
    
    if (file.size > maxSizeBytes) {
      analysisStore.error = `Arquivo muito grande. Tamanho máximo: ${maxSize}MB`
    } else {
      analysisStore.error = 'Arquivo muito pequeno. Tamanho mínimo: 1KB'
    }
    return
  }

  selectedFile.value = file
}

function clearFile() {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  analysisStore.clearError()
}

async function uploadFile() {
  if (!selectedFile.value) {
    console.log('❌ Componente: Nenhum arquivo selecionado')
    return
  }

  console.log('🔄 Componente: Iniciando upload do arquivo:', selectedFile.value.name)
  
  try {
    const response = await analysisStore.uploadImage(selectedFile.value)
    
    // Limpar arquivo selecionado após upload bem-sucedido
    clearFile()
    
    // Emitir evento de sucesso (opcional)
    console.log('✅ Componente: Upload realizado com sucesso:', response)
  } catch (err) {
    console.error('❌ Componente: Erro no upload:', err)
  }
}

</script>
