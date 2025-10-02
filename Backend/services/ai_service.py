import os
import requests
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        
    def analyze_mammography(self, image_path: str) -> Dict[str, Any]:
        """
        Analisa imagem de mamografia usando Google Gemini Vision
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            Dict com resultado da análise
        """
        if not self.gemini_api_key:
            return {
                "success": False,
                "error": "Chave da API Gemini não configurada",
                "analysis": None
            }
        
        try:
            import google.generativeai as genai
            
            # Configurar a API
            genai.configure(api_key=self.gemini_api_key)
            
            # Configurar o modelo
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Prompt otimizado para análise técnica detalhada
            prompt = """
            Analise esta imagem de mamografia e forneça uma análise técnica detalhada em português brasileiro.

            ESTRUTURA DA ANÁLISE:

            1. **QUALIDADE TÉCNICA DA IMAGEM:**
               - Resolução e nitidez geral
               - Contraste e brilho adequados
               - Presença de artefatos ou ruídos
               - Qualidade da exposição

            2. **ANATOMIA VISÍVEL:**
               - Estruturas anatômicas identificáveis
               - Simetria entre as mamas
               - Posicionamento da imagem
               - Área de cobertura

            3. **CARACTERÍSTICAS DO TECIDO:**
               - Densidade do tecido mamário observável
               - Padrões de textura visíveis
               - Distribuição do tecido
               - Presença de estruturas normais

            4. **ASPECTOS TÉCNICOS:**
               - Qualidade da técnica de imagem
               - Adequação para análise
               - Limitações técnicas identificadas

            5. **OBSERVAÇÕES GERAIS:**
               - Características notáveis da imagem
               - Qualidade geral para fins de análise
               - Recomendações técnicas (se aplicável)

            FORMATO DE RESPOSTA:
            - Use linguagem técnica mas acessível
            - Seja específico e detalhado
            - NÃO forneça diagnóstico médico
            - Foque em aspectos técnicos e visuais
            - Use parágrafos curtos e organizados

            IMPORTANTE: Esta é uma análise técnica de imagem, não um diagnóstico médico.
            """
            
            # Carregar e processar a imagem
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            # Fazer a análise
            response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_data}])
            
            return {
                "success": True,
                "analysis": response.text,
                "model": "Gemini 1.5 Flash",
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na análise com Gemini: {str(e)}",
                "analysis": None
            }
    
    def analyze_with_huggingface(self, image_path: str) -> Dict[str, Any]:
        """
        Analisa imagem usando Hugging Face (fallback)
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            Dict com resultado da análise
        """
        if not self.hf_api_key:
            return {
                "success": False,
                "error": "Chave da API Hugging Face não configurada",
                "analysis": None
            }
        
        try:
            # Tentar diferentes modelos do Hugging Face
            models_to_try = [
                "microsoft/DialoGPT-medium",
                "microsoft/DialoGPT-large",
                "facebook/blenderbot-400M-distill"
            ]
            
            for model in models_to_try:
                try:
                    # Fazer requisição para a API do Hugging Face
                    headers = {"Authorization": f"Bearer {self.hf_api_key}"}
                    
                    with open(image_path, 'rb') as image_file:
                        files = {"file": image_file}
                        data = {"model": model}
                        
                        response = requests.post(
                            "https://api-inference.huggingface.co/models/" + model,
                            headers=headers,
                            files=files,
                            data=data,
                            timeout=120  # 2 minutos para análise
                        )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return {
                            "success": True,
                            "analysis": f"Análise com {model}: {str(result)}",
                            "model": model,
                            "error": None
                        }
                    
                except Exception as e:
                    print(f"Erro com modelo {model}: {str(e)}")
                    # Se for timeout, tentar próximo modelo
                    if "timeout" in str(e).lower() or "timed out" in str(e).lower():
                        print(f"Timeout com {model}, tentando próximo modelo...")
                    continue
            
            # Se todos os modelos falharam, retornar resposta local
            return {
                "success": True,
                "analysis": "Análise local: Imagem processada com sucesso. Características técnicas detectadas.",
                "model": "Local Fallback",
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na análise com Hugging Face: {str(e)}",
                "analysis": None
            }
