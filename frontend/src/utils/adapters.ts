/**
 * Adapters para conversão de dados entre backend e frontend
 * Converte snake_case do backend para camelCase do frontend
 */

/**
 * Converte uma string de snake_case para camelCase
 * @param str - String em snake_case
 * @returns String em camelCase
 */
function snakeToCamel(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
}

/**
 * Converte um objeto de snake_case para camelCase
 * @param obj - Objeto com propriedades em snake_case
 * @returns Objeto com propriedades em camelCase
 */
function convertKeysToCamelCase<T>(obj: any): T {
  if (obj === null || obj === undefined) {
    return obj
  }

  if (Array.isArray(obj)) {
    return obj.map(convertKeysToCamelCase) as T
  }

  if (typeof obj === 'object') {
    const converted: any = {}
    for (const [key, value] of Object.entries(obj)) {
      const camelKey = snakeToCamel(key)
      converted[camelKey] = convertKeysToCamelCase(value)
    }
    return converted
  }

  return obj
}

/**
 * Converte uma análise do formato backend para frontend
 * @param analysis - Análise em formato backend (snake_case)
 * @returns Análise em formato frontend (camelCase)
 */
export function adaptAnalysis(analysis: any): any {
  return convertKeysToCamelCase(analysis)
}

/**
 * Converte uma lista de análises do formato backend para frontend
 * @param analyses - Lista de análises em formato backend
 * @returns Lista de análises em formato frontend
 */
export function adaptAnalyses(analyses: any[]): any[] {
  return analyses.map(adaptAnalysis)
}

/**
 * Converte uma resposta de upload do formato backend para frontend
 * @param response - Resposta em formato backend
 * @returns Resposta em formato frontend
 */
export function adaptUploadResponse(response: any): any {
  return convertKeysToCamelCase(response)
}

/**
 * Converte uma resposta de análise do formato backend para frontend
 * @param response - Resposta em formato backend
 * @returns Resposta em formato frontend
 */
export function adaptAnalysisResponse(response: any): any {
  return convertKeysToCamelCase(response)
}
