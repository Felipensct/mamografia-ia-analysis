/**
 * Utilitários para manipulação de imagens
 * Centraliza funções relacionadas a imagens para evitar duplicação
 */

/**
 * Placeholder SVG para quando uma imagem falha ao carregar
 */
export const IMAGE_PLACEHOLDER_SVG = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCA2NCA2NCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjY0IiBoZWlnaHQ9IjY0IiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0yNCAyNEg0MFY0MEgyNFYyNFoiIGZpbGw9IiNEMUQ1REIiLz4KPC9zdmc+'

/**
 * Handler para erro de carregamento de imagem
 * Substitui a imagem por um placeholder quando falha ao carregar
 * @param event - Evento de erro da imagem
 */
export function handleImageError(event: Event): void {
  const img = event.target as HTMLImageElement
  console.warn('⚠️ Erro ao carregar imagem:', {
    src: img.src,
    alt: img.alt,
    naturalWidth: img.naturalWidth,
    naturalHeight: img.naturalHeight
  })
  img.src = IMAGE_PLACEHOLDER_SVG
}

/**
 * Retorna as dimensões de uma imagem como string formatada
 * @param dimensions - Array com [largura, altura]
 * @returns String formatada (ex: "1920x1080px")
 */
export function formatImageDimensions(dimensions: [number, number] | undefined): string {
  if (!dimensions) return 'N/A'
  const [width, height] = dimensions
  return `${width}x${height}px`
}

/**
 * Valida se um arquivo é uma imagem válida
 * @param file - Arquivo a ser validado
 * @returns true se é uma imagem válida
 */
export function isValidImageFile(file: File): boolean {
  const allowedTypes = [
    'image/png',
    'image/jpeg',
    'image/jpg',
    'image/tiff',
    'image/bmp',
    'application/dicom'
  ]

  const allowedExtensions = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.dcm']
  const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()

  return allowedTypes.includes(file.type) || allowedExtensions.includes(fileExtension)
}

/**
 * Valida o tamanho de um arquivo
 * @param file - Arquivo a ser validado
 * @param maxSizeBytes - Tamanho máximo em bytes (padrão: 50MB para DICOM, 10MB para outros)
 * @param minSizeBytes - Tamanho mínimo em bytes (padrão: 1KB)
 * @returns true se o tamanho é válido
 */
export function isValidFileSize(
  file: File,
  maxSizeBytes?: number,
  minSizeBytes: number = 1024
): boolean {
  // Definir limite baseado no tipo de arquivo
  if (!maxSizeBytes) {
    const isDicom = file.name.toLowerCase().endsWith('.dcm') || file.type === 'application/dicom'
    maxSizeBytes = isDicom ? 50 * 1024 * 1024 : 10 * 1024 * 1024 // 50MB para DICOM, 10MB para outros
  }

  return file.size >= minSizeBytes && file.size <= maxSizeBytes
}

/**
 * Cria uma URL de preview para um arquivo
 * @param file - Arquivo para criar preview
 * @returns URL do preview
 */
export function createImagePreview(file: File): string {
  return URL.createObjectURL(file)
}

/**
 * Limpa uma URL de preview para liberar memória
 * @param url - URL do preview a ser limpa
 */
export function revokeImagePreview(url: string): void {
  URL.revokeObjectURL(url)
}
