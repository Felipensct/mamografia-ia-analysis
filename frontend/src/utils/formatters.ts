/**
 * Utilitários de formatação para o projeto Mamografia IA
 * Centraliza funções comuns de formatação para evitar duplicação
 */

/**
 * Formata um tamanho de arquivo em bytes para uma string legível
 * @param bytes - Tamanho em bytes
 * @returns String formatada (ex: "1.5 MB")
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * Formata uma data ISO para o formato brasileiro
 * @param dateString - Data em formato ISO string
 * @returns String formatada (ex: "25/12/2024 14:30")
 */
export function formatDate(dateString: string): string {
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

/**
 * Retorna as classes CSS para badges de status
 * @param status - Status da análise
 * @returns Classes CSS para o badge
 */
export function getStatusBadgeClass(status: string): string {
  const classes: Record<string, string> = {
    uploaded: 'bg-blue-100 text-blue-800',
    processing: 'bg-yellow-100 text-yellow-800',
    completed: 'bg-green-100 text-green-800',
    error: 'bg-red-100 text-red-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

/**
 * Retorna o texto do status traduzido
 * @param status - Status da análise
 * @returns Texto do status em português
 */
export function getStatusText(status: string): string {
  const texts: Record<string, string> = {
    uploaded: 'Enviado',
    processing: 'Processando',
    completed: 'Concluído',
    error: 'Erro'
  }
  return texts[status] || status
}

/**
 * Retorna as classes CSS para badges de status (versão moderna)
 * @param status - Status da análise
 * @returns Classes CSS para o badge moderno
 */
export function getStatusBadgeClassModern(status: string): string {
  const classes: Record<string, string> = {
    uploaded: 'status-badge status-uploaded',
    processing: 'status-badge status-processing',
    completed: 'status-badge status-completed',
    error: 'status-badge status-error'
  }
  return classes[status] || 'status-badge status-uploaded'
}

/**
 * Retorna as classes CSS para gradientes de status
 * @param status - Status da análise
 * @returns Gradiente CSS para o status
 */
export function getStatusGradient(status: string): string {
  const gradients: Record<string, string> = {
    uploaded: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
    processing: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    completed: 'linear-gradient(135deg, #16a34a 0%, #15803d 100%)',
    error: 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)'
  }
  return gradients[status] || gradients.uploaded
}

/**
 * Retorna as classes CSS para dots de status
 * @param status - Status da análise
 * @returns Classes CSS para o dot de status
 */
export function getStatusDotClass(status: string): string {
  const dotClasses: Record<string, string> = {
    uploaded: 'dot-primary',
    processing: 'dot-warning',
    completed: 'dot-success',
    error: 'dot-danger'
  }
  return dotClasses[status] || 'dot-primary'
}
