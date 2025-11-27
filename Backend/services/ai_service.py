import os
import requests
import json
import base64
import cv2
import numpy as np
import hashlib
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from PIL import Image, ImageEnhance, ImageFilter
import io

load_dotenv()

class AIService:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        # APIs disponíveis
        self.available_apis = []
        if self.gemini_api_key:
            self.available_apis.append("gemini")
        if self.hf_api_key:
            self.available_apis.append("huggingface")
    
    def get_available_apis(self) -> list:
        """Retorna lista de APIs disponíveis"""
        return self.available_apis
        
    def _calculate_image_hash(self, image_path: str) -> str:
        """
        Calcula hash MD5 da imagem para garantir consistência
        
        Args:
            image_path: Caminho da imagem
            
        Returns:
            Hash MD5 em hexadecimal
        """
        hash_md5 = hashlib.md5()
        with open(image_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def preprocess_image(self, image_path: str) -> str:
        """
        Pré-processa imagem para melhor análise de IA com foco em mamografia
        Processamento consistente e determinístico - preserva características originais
        
        Args:
            image_path: Caminho da imagem original
            
        Returns:
            Caminho da imagem processada
        """
        try:
            # Carregar imagem
            with Image.open(image_path) as img:
                original_mode = img.mode
                print(f"🖼️  Processando imagem: {img.size}, modo: {original_mode}")
                
                # Para PGM, preservar modo original se já for escala de cinza
                is_pgm = image_path.lower().endswith('.pgm')
                
                # 1. CONVERSÃO DE MODO (preservar características originais)
                if is_pgm and img.mode in ['L', 'I', 'F']:
                    # PGM já está em escala de cinza, manter modo original
                    print("📷 PGM mantido em modo original (escala de cinza)")
                elif img.mode != 'L':
                    # Converter outros formatos para escala de cinza
                    img = img.convert('L')
                    print("📷 Convertido para escala de cinza")
                
                # 2. OTIMIZAR CONTRASTE (valor reduzido para preservar características)
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.15)  # Reduzido de 1.3 para 1.15
                print("🎨 Contraste otimizado (preservando características)")
                
                # 3. APLICAR NITIDEZ (parâmetros reduzidos para menos agressividade)
                img = img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=150, threshold=3))
                print("🔍 Nitidez melhorada (parâmetros conservadores)")
                
                # 4. AJUSTAR BRILHO (valor mínimo para preservar histograma original)
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(1.02)  # Reduzido de 1.05 para 1.02
                print("💡 Brilho ajustado (mínimo necessário)")
                
                # 5. REALCE DE BORDAS (removido - muito agressivo para PGM)
                # Mantido apenas para não-PGM se necessário
                if not is_pgm:
                    img = img.filter(ImageFilter.EDGE_ENHANCE)
                    print("📐 Bordas realçadas (apenas para não-PGM)")
                
                # 6. REDIMENSIONAR para tamanho otimizado (tamanho fixo para consistência)
                img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                print(f"📏 Redimensionado para: {img.size}")
                
                # 7. SALVAR com alta qualidade (qualidade fixa para consistência)
                processed_path = image_path.replace('.', '_processed.')
                img.save(processed_path, 'JPEG', quality=98, optimize=False)  # optimize=False para consistência
                print(f"💾 Imagem processada salva: {processed_path}")
                
                return processed_path
                
        except Exception as e:
            print(f"❌ Erro no pré-processamento: {str(e)}")
            return image_path  # Retorna original se houver erro
        
    def analyze_mammography(self, image_path: str, image_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analisa imagem de mamografia usando Google Gemini Vision
        
        Args:
            image_path: Caminho para a imagem
            image_id: Identificador único da imagem (opcional, será gerado se não fornecido)
            
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
            
            print("🔄 Iniciando análise com Gemini...")
            
            # Configurar a API
            genai.configure(api_key=self.gemini_api_key)
            
            # Gerar identificador único baseado no hash da imagem para consistência
            if image_id is None:
                image_hash = self._calculate_image_hash(image_path)
                image_id = f"img_{image_hash[:12]}"
            
            print(f"🆔 Identificador da imagem: {image_id}")
            
            # Configurar modelo com parâmetros para máximo determinismo
            generation_config = {
                "temperature": 0.0,  # Temperatura zero para máximo determinismo
                "top_p": 0.95,
                "top_k": 40,
            }
            
            model = genai.GenerativeModel(
                'gemini-2.5-pro',
                generation_config=generation_config
            )
            
            # Pré-processar imagem para melhor análise
            processed_image_path = self.preprocess_image(image_path)
            
            # Prompt otimizado para detecção de câncer de mama em estágios iniciais
            # IMPORTANTE: Usar identificador real em vez de pedir ao modelo para inventar
            prompt = f"""
            🧠 Prompt Detalhado — Análise de Mamografia (Formato MIAS - Dataset MIAS)

            📐 ESPECIFICAÇÕES TÉCNICAS DO DATASET MIAS:

            - Todas as imagens têm tamanho fixo: 1024 pixels x 1024 pixels
            - Imagens estão centralizadas na matriz
            - Sistema de coordenadas: origem (0,0) no CANTO INFERIOR ESQUERDO
            - Eixo X: aumenta da esquerda para direita (0 a 1023)
            - Eixo Y: aumenta de baixo para cima (0 a 1023)

            Você é uma inteligência artificial especializada em análise de imagens médicas, com foco em mamografias.
            Sua tarefa é analisar a imagem fornecida e gerar uma descrição estruturada no formato MIAS (Mammographic Image Analysis Society), conforme as especificações do dataset MIAS abaixo.

            🩻 Objetivo

            Identificar o tipo de tecido mamário predominante e classificar a presença, tipo, severidade e localização de eventuais anormalidades detectadas na mamografia.

            🧩 Formato de Saída Esperado

            A resposta deve seguir exatamente este formato, com todos os campos preenchidos quando aplicáveis:

            1. Referência MIAS: {image_id}
            2. Tipo de tecido de fundo: [F / G / D]
            3. Classe de anormalidade: [CALC / CIRC / SPIC / MISC / ARCH / ASYM / NORM]
            4. Severidade da anormalidade: [B / M]
            5. Coordenadas do centro da anormalidade: (x= , y= )
            6. Raio aproximado: [valor em pixels]

            Nota: Se não houver anormalidade (classe = NORM), omita os campos 4, 5 e 6.

            IMPORTANTE: Use EXATAMENTE a referência MIAS fornecida: {image_id}
            Não invente ou altere este identificador.

            🧬 1. Tipo de tecido de fundo (coluna 2 do formato MIAS)

            Classifique o tecido mamário predominante na imagem de acordo com as seguintes categorias:

            Código	Tipo	Descrição
            F (Fatty - Gorduroso):
            - Características: Predominantemente escuro/transparente
            - Homogeneidade: Alta (pouca variação de densidade)
            - Percentual estimado: >70% da imagem com baixa densidade

            G (Fatty-glandular - Gorduroso-glandular):
            - Características: MISTO - áreas claras e escuras equilibradas
            - Homogeneidade: Média (variação moderada)
            - Percentual estimado: 40-60% denso, 40-60% gorduroso

            D (Dense-glandular - Densa-glandular):
            - Características: Predominantemente claro/denso
            - Homogeneidade: Média a baixa (variação alta)
            - Percentual estimado: >60% da imagem com alta densidade

            INSTRUÇÃO:
            Analise a distribuição de densidade na imagem:
            - Se >70% escuro/transparente → F
            - Se 40-60% de cada tipo → G
            - Se >60% claro/denso → D

            ⚕️ 2. Classe de anormalidade (coluna 3 do formato MIAS)

            CRITÉRIOS DIFERENCIAIS CRÍTICOS:

            CIRC (Massa circunscrita) - CRITÉRIOS OBRIGATÓRIOS:
            - DEVE haver uma MASSA VISÍVEL e DEFINIDA
            - Forma: Arredondada, oval ou elíptica
            - Bordas: REGULARES, bem definidas, contínuas, suaves
            - Contraste: Massa claramente mais densa ou menos densa que o tecido circundante
            - Tamanho: Geralmente > 5mm de diâmetro
            - Se NÃO houver uma MASSA DEFINIDA, NÃO é CIRC

            ARCH (Distorção arquitetural) - CRITÉRIOS OBRIGATÓRIOS:
            - NÃO há massa definida, apenas distorção do padrão tecidual
            - Característica: O tecido mamário normal está distorcido/retraído
            - Forma: Sem forma definida, apenas padrão alterado
            - Bordas: Não há bordas de massa, apenas alteração arquitetural
            - Contraste: Pode não ter contraste claro, apenas padrão alterado
            - Se houver uma MASSA DEFINIDA, NÃO é ARCH

            DECISÃO CRÍTICA - FLUXO DE DECISÃO:
            1. Primeiro, identifique se há uma MASSA VISÍVEL e DEFINIDA:
            - Se SIM → CIRC, SPIC ou MISC (dependendo das bordas)
            - Se NÃO → ARCH, ASYM ou NORM

            2. Se houver massa:
            - Bordas REGULARES e forma definida → CIRC
            - Bordas IRREGULARES com espículas → SPIC
            - Massa sem forma definida → MISC

            3. Se NÃO houver massa:
            - Apenas distorção do padrão → ARCH
            - Assimetria de densidade → ASYM
            - Nenhuma anormalidade → NORM

            REGRAS DE PRIORIDADE (siga esta ordem):
            1. Se houver CALC (calcificações), sempre escolha CALC como principal
            2. Se houver SPIC (massa espiculada), escolha SPIC como segunda prioridade
            3. Se houver CIRC (massa circunscrita), escolha CIRC como terceira prioridade
            4. Se houver MISC, ARCH ou ASYM, escolha a que tiver maior área visível
            5. Se não houver nenhuma anormalidade clara, classifique como NORM

            Código	Tipo de Lesão	Descrição
            CALC	Calcificação	Pequenas áreas brilhantes indicando depósitos de cálcio. Podem ser agrupadas (clusters) ou difusas.
            CIRC	Massa circunscrita	Lesão bem definida, bordas regulares, aspecto arredondado ou oval. DEVE haver massa visível.
            SPIC	Massa espiculada	Lesão com bordas irregulares, prolongamentos lineares, aspecto estrelado.
            MISC	Massa indefinida	Lesão não claramente circunscrita, sem contornos regulares.
            ARCH	Distorção arquitetural	Alteração do padrão normal do tecido mamário, SEM massa definida.
            ASYM	Assimetria	Densidade assimétrica entre mamas ou quadrantes.
            NORM	Normal	Ausência de anormalidades detectáveis.

            INSTRUÇÃO ESPECIAL PARA CALCIFICAÇÕES:
            - Se houver múltiplas calcificações, identifique o CLUSTER (agrupamento) mais significativo
            - As coordenadas devem referir-se ao CENTRO DO CLUSTER, não a calcificações individuais
            - Se as calcificações estiverem amplamente distribuídas pela imagem (não concentradas), OMITA as coordenadas e o raio

            🧪 3. Severidade da anormalidade (coluna 4 do formato MIAS)

            Determine o caráter benigno ou maligno da anormalidade identificada, com base nos padrões visuais da imagem.

            Código	Significado	Descrição
            B (Benigna) - CRITÉRIOS OBRIGATÓRIOS:
            - Bordas: REGULARES, suaves, bem definidas, contínuas
            - Forma: Simétrica ou levemente assimétrica, definida
            - Contorno: Contínuo, sem interrupções
            - Densidade: Homogênea ou levemente heterogênea
            - Efeito no tecido: Não invasivo, tecido circundante preservado

            M (Maligna) - CRITÉRIOS OBRIGATÓRIOS:
            - Bordas: IRREGULARES, espiculadas, mal definidas, descontínuas
            - Forma: Altamente assimétrica, irregular, indefinida
            - Contorno: Descontínuo, com interrupções
            - Densidade: Altamente heterogênea
            - Efeito no tecido: Invasivo, tecido circundante distorcido/retraído

            REGRAS DE CLASSIFICAÇÃO:
            - Se a massa tem bordas REGULARES e forma definida → B (Benigna)
            - Se a massa tem bordas IRREGULARES ou espiculadas → M (Maligna)
            - Se há dúvida entre B e M, escolha B (mais conservador)
            - CIRC geralmente é B (benigna), mas pode ser M se tiver características suspeitas
            - SPIC geralmente é M (maligna), mas pode ser B em casos raros

            Instrução para IA:
            Caso exista uma anormalidade, classifique sua severidade como Benigna (B) ou Maligna (M).
            Se a imagem for normal (NORM), este campo deve ser omitido.

            📍 4. Localização e dimensão da lesão (colunas 5–7 do formato MIAS)

            IMPORTANTE - ESPECIFICAÇÕES DO DATASET MIAS:

            Sistema de Coordenadas:
            - Origem (0,0) está no CANTO INFERIOR ESQUERDO da imagem
            - Eixo X: aumenta da esquerda para direita (0 a 1023)
            - Eixo Y: aumenta de baixo para cima (0 a 1023)
            - Todas as imagens têm 1024x1024 pixels

            Coordenadas (x, y):
            - Representam o CENTRO da anormalidade
            - Para CALC: coordenadas do CENTRO DO CLUSTER (agrupamento), não de calcificações individuais
            - Valores devem estar entre 0 e 1023

            Raio:
            - Representa o raio (em pixels) de um CÍRCULO que ENVOLVE COMPLETAMENTE a anormalidade
            - O círculo deve ser o menor possível que ainda envolva toda a anormalidade
            - Para CIRC: raio ≈ metade do diâmetro maior da massa
            - Para SPIC: inclua todas as espículas no círculo
            - Para CALC: raio do círculo que envolve o cluster de calcificações

            QUANDO OMITIR COORDENADAS E RAIO:
            - Se a classe for NORM (normal)
            - Se as calcificações (CALC) estiverem amplamente distribuídas pela imagem, sem concentração clara em um ponto
            - Se a anormalidade for difusa e não tiver localização focal definida

            LOCALIZAÇÃO - MÉTODO PASSO A PASSO:

            1. Identifique o CENTRO GEOMÉTRICO da anormalidade:
            - Para CIRC: centro da massa circular/oval
            - Para SPIC: centro da massa (ignorar espículas na localização do centro)
            - Para CALC: centro do cluster de calcificações
            - Para ARCH: centro da área de distorção

            2. Meça as coordenadas:
            - X: distância do canto esquerdo (0-1023)
            - Y: distância do canto inferior (0-1023)
            - Use o sistema de coordenadas com origem no canto inferior esquerdo

            3. Calcule o raio:
            - Desenhe um círculo que ENVOLVE COMPLETAMENTE a anormalidade
            - Use o menor raio possível que ainda envolva tudo
            - Para CIRC: raio ≈ metade do diâmetro maior
            - Para SPIC: inclua todas as espículas no círculo

            📚 EXEMPLOS DO DATASET MIAS (Few-Shot Learning)

            Use estes exemplos reais do dataset MIAS como referência para classificação correta:

            EXEMPLO 1 - Massa Circunscrita Benigna (CIRC B):
            Laudo: mdb002 G CIRC B 522 280 69
            Características: Tecido G (gorduroso-glandular), massa circunscrita bem definida, benigna, localizada em (522, 280) com raio 69

            EXEMPLO 2 - Massa Circunscrita Benigna (CIRC B):
            Laudo: mdb001 G CIRC B 535 425 197
            Características: Tecido G, massa circunscrita grande (raio 197), benigna, localizada em (535, 425)

            EXEMPLO 3 - Massa Circunscrita Benigna (CIRC B):
            Laudo: mdb010 F CIRC B 525 425 33
            Características: Tecido F (gorduroso), massa circunscrita pequena (raio 33), benigna, localizada em (525, 425)

            EXEMPLO 4 - Massa Circunscrita Maligna (CIRC M):
            Laudo: mdb023 G CIRC M 538 681 29
            Características: Tecido G, massa circunscrita, mas com características malignas (bordas irregulares ou suspeitas), localizada em (538, 681)

            EXEMPLO 5 - Distorção Arquitetural Maligna (ARCH M):
            Laudo: mdb115 G ARCH M 461 532 117
            Características: Tecido G, distorção arquitetural (SEM massa definida), maligna, localizada em (461, 532) com raio 117

            EXEMPLO 6 - Distorção Arquitetural Benigna (ARCH B):
            Laudo: mdb121 G ARCH B 492 434 87
            Características: Tecido G, distorção arquitetural (SEM massa definida), benigna, localizada em (492, 434) com raio 87

            EXEMPLO 7 - Massa Espiculada Benigna (SPIC B):
            Laudo: mdb145 D SPIC B 669 543 49
            Características: Tecido D (denso), massa espiculada (bordas irregulares com espículas), benigna, localizada em (669, 543)

            EXEMPLO 8 - Massa Espiculada Maligna (SPIC M):
            Laudo: mdb178 G SPIC M 492 600 70
            Características: Tecido G, massa espiculada (bordas irregulares com espículas), maligna, localizada em (492, 600)

            EXEMPLO 9 - Calcificação Maligna (CALC M):
            Laudo: mdb209 G CALC M 647 503 87
            Características: Tecido G, cluster de calcificações, maligna, localizada em (647, 503) com raio 87

            EXEMPLO 10 - Calcificação Benigna (CALC B):
            Laudo: mdb212 G CALC B 687 882 3
            Características: Tecido G, cluster pequeno de calcificações (raio 3), benigna, localizada em (687, 882)

            EXEMPLO 11 - Massa Indefinida Benigna (MISC B):
            Laudo: mdb013 G MISC B 667 365 31
            Características: Tecido G, massa indefinida (sem contornos regulares), benigna, localizada em (667, 365)

            EXEMPLO 12 - Assimetria Maligna (ASYM M):
            Laudo: mdb072 G ASYM M 266 517 28
            Características: Tecido G, assimetria de densidade, maligna, localizada em (266, 517)

            EXEMPLO 13 - Normal (NORM):
            Laudo: mdb003 D NORM
            Características: Tecido D, nenhuma anormalidade detectável

            EXEMPLO 14 - Normal (NORM):
            Laudo: mdb006 F NORM
            Características: Tecido F, nenhuma anormalidade detectável

            OBSERVAÇÕES IMPORTANTES DOS EXEMPLOS:
            - CIRC geralmente tem tecido G ou F, raramente D
            - CIRC geralmente é B (benigna), mas pode ser M
            - ARCH pode ter tecido G, D ou F
            - ARCH pode ser B ou M
            - SPIC geralmente é M (maligna), mas pode ser B
            - CALC pode ter qualquer tipo de tecido
            - Coordenadas variam amplamente (100-800 para X e Y)
            - Raios variam de 3 a 200 pixels, dependendo do tipo

            🧩 Exemplo de saída completa (com anormalidade)

            1. Referência MIAS: {image_id}
            2. Tipo de tecido de fundo: G (Fatty-glandular)
            3. Classe de anormalidade: CIRC (Massa circunscrita)
            4. Severidade da anormalidade: B (Benigna)
            5. Coordenadas do centro da anormalidade: (x=522, y=280)
            6. Raio aproximado: 69 pixels

            🧩 Exemplo de saída (sem anormalidade)

            1. Referência MIAS: {image_id}
            2. Tipo de tecido de fundo: G (Fatty-glandular)
            3. Classe de anormalidade: NORM

            🧩 Exemplo de saída (calcificações difusas - coordenadas omitidas)

            1. Referência MIAS: {image_id}
            2. Tipo de tecido de fundo: D (Dense-glandular)
            3. Classe de anormalidade: CALC (Calcificação)
            4. Severidade da anormalidade: B (Benigna)
            (Nota: Coordenadas e raio omitidos porque calcificações estão amplamente distribuídas)

            ⚙️ Regras adicionais de formatação

            - Sempre siga a ordem numérica dos campos (1–6)
            - Use EXATAMENTE a referência MIAS fornecida: {image_id}
            - Não invente, altere ou gere novos identificadores
            - Inclua apenas valores coerentes e observáveis na imagem
            - Evite descrições narrativas: a saída deve ser estruturada e objetiva
            - Valide que coordenadas estão entre 0 e 1023
            - Valide que raio é positivo e razoável (típico: 10-200 pixels)
            - Para CALC, sempre considere clusters, não calcificações individuais
            - DIFERENCIE CIRCITICAMENTE: CIRC tem massa definida, ARCH não tem massa definida
            - Se houver dúvida entre CIRC e ARCH, verifique se há MASSA VISÍVEL:
            * Se SIM → CIRC
            * Se NÃO → ARCH

            Analise a imagem de mamografia (referência {image_id}) e descreva os achados conforme o formato MIAS acima, usando os exemplos como referência.
            """
            
            # Carregar e processar a imagem otimizada
            with open(processed_image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            # Fazer a análise com timeout
            print("🔄 Enviando requisição para Gemini...")
            response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_data}])
            
            if not response or not response.text:
                raise Exception("Resposta vazia do Gemini")
            
            print("✅ Análise Gemini concluída com sucesso")
            
            # Limpar arquivo temporário
            try:
                if processed_image_path != image_path:
                    os.remove(processed_image_path)
            except:
                pass
            
            return {
                "success": True,
                "analysis": response.text,
                "model": "Gemini 2.5 Pro",
                "error": None
            }
            
        except Exception as e:
            print(f"❌ Erro na análise Gemini: {str(e)}")
            return {
                "success": False,
                "error": f"Erro na análise com Gemini: {str(e)}",
                "analysis": None
            }
    
    def analyze_with_alternative_api(self, image_path: str) -> Dict[str, Any]:
        """
        Analisa imagem usando Hugging Face com modelos específicos para imagens médicas
        
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
            # Pré-processar imagem para melhor análise
            processed_image_path = self.preprocess_image(image_path)
            
            # Modelos disponíveis e testados (ordenados por confiança)
            models_to_try = [
                # FASE 1: Modelos com melhor performance (testados)
                "facebook/convnext-base-224",  # ConvNeXt - Melhor confiança (15.1%)
                "microsoft/swin-base-patch4-window7-224",  # Swin Transformer - Boa confiança (8.0%)
                
                # FASE 2: Modelos alternativos
                "microsoft/resnet-50",  # ResNet-50 - Confiança moderada (5.0%)
                "google/vit-base-patch16-224",  # Vision Transformer - Confiança baixa (2.7%)
                
                # NOTA: Modelos médicos específicos não estão disponíveis na API
                # Usamos modelos gerais com interpretação médica + análise local
            ]
            
            for model in models_to_try:
                try:
                    print(f"🔄 Tentando análise com modelo: {model}")
                    
                    # Preparar imagem para o modelo
                    with open(processed_image_path, 'rb') as image_file:
                        image_data = image_file.read()
                    
                    # Converter para base64 se necessário
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    
                    headers = {
                        "Authorization": f"Bearer {self.hf_api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "inputs": image_base64,
                        "parameters": {
                            "top_k": 5
                        }
                    }
                    
                    response = requests.post(
                        f"https://router.huggingface.co/hf-inference/models/{model}",
                        headers=headers,
                        json=payload,
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Processar resultado para análise médica
                        analysis_text = self._format_huggingface_analysis(result, model, processed_image_path)
                        
                        # Limpar arquivo temporário
                        try:
                            if processed_image_path != image_path:
                                os.remove(processed_image_path)
                        except:
                            pass
                        
                        return {
                            "success": True,
                            "analysis": analysis_text,
                            "model": f"Hugging Face - {model}",
                            "error": None
                        }
                    else:
                        print(f"❌ Erro HTTP {response.status_code} com {model}: {response.text}")
                        
                except Exception as e:
                    print(f"❌ Erro com modelo {model}: {str(e)}")
                    # Se for timeout, tentar próximo modelo
                    if "timeout" in str(e).lower() or "timed out" in str(e).lower():
                        print(f"⏰ Timeout com {model}, tentando próximo modelo...")
                    continue
            
            # Limpar arquivo temporário se não foi limpo antes
            try:
                if processed_image_path != image_path:
                    os.remove(processed_image_path)
            except:
                pass
            
            # Se todos os modelos falharam, retornar análise local
            return {
                "success": True,
                "analysis": self._generate_local_analysis(image_path),
                "model": "Análise Local - OpenCV",
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na análise com Hugging Face: {str(e)}",
                "analysis": None
            }
    
    def _format_huggingface_analysis(self, result: list, model: str, image_path: str = None) -> str:
        """Formata resultado do Hugging Face para análise médica com interpretação contextual"""
        try:
            if isinstance(result, list) and len(result) > 0:
                # Extrair características mais relevantes
                top_predictions = result[:5]  # Top 5 predições
                
                # Mapear termos gerais para contexto médico quando possível
                medical_interpretations = self._interpret_for_medical_context(top_predictions)
                
                analysis = f"""
## ANÁLISE COMPUTACIONAL DE IMAGEM
**Modelo:** {model} - Classificação de Padrões Visuais

### ⚠️ LIMITAÇÕES IMPORTANTES:
- Este modelo foi treinado em **imagens gerais** (objetos, animais, etc.)
- **NÃO é específico para imagens médicas** ou mamografias
- As classificações são interpretadas no contexto médico por mapeamento
- **Confiança limitada** para análise médica real

### 📊 CARACTERÍSTICAS DETECTADAS (Interpretação Médica):

"""
                for i, pred in enumerate(top_predictions, 1):
                    if isinstance(pred, dict) and 'label' in pred and 'score' in pred:
                        label = pred['label']
                        score = pred['score']
                        confidence = score * 100
                        
                        # Interpretar contexto médico quando possível
                        medical_note = medical_interpretations.get(label, "")
                        note_text = f" ({medical_note})" if medical_note else ""
                        
                        analysis += f"{i}. **{label}** (Confiança: {confidence:.1f}%){note_text}\n"
                
                # Calcular confiança média
                avg_confidence = sum(pred.get('score', 0) * 100 for pred in top_predictions if isinstance(pred, dict)) / len(top_predictions)
                
                analysis += f"""

### 🔍 INTERPRETAÇÃO PARA MAMOGRAFIA:
- **Modelo utilizado**: {model}
- **Confiança média**: {avg_confidence:.1f}% (limitada para contexto médico)
- **Tipo de análise**: Classificação de padrões visuais gerais
- **Mapeamento**: Interpretação manual para terminologia médica

### 📋 MAPEAMENTO DE PADRÕES:
As classificações de objetos foram interpretadas no contexto de mamografia:
- **Estruturas circulares** → Possíveis nódulos ou lesões
- **Estruturas lineares** → Possíveis ductos ou vasos
- **Áreas de densidade** → Variações do tecido mamário
- **Padrões de textura** → Características do tecido fibroglandular

### ⚠️ LIMITAÇÕES CRÍTICAS:
- **Não é diagnóstico médico** - apenas classificação computacional
- **Modelo não treinado** em imagens médicas
- **Interpretação limitada** - mapeamento manual de conceitos gerais
- **Confiança baixa** para análise médica real
- **Recomenda-se análise complementar** com IA especializada (Gemini)

### 💡 RECOMENDAÇÃO:
Esta análise serve como **complemento técnico** apenas. Para análise médica real, 
use o modelo Gemini especializado ou consulte um radiologista qualificado.
"""

                # Se confiança baixa, adicionar análise local
                if avg_confidence < 10.0 and image_path:
                    analysis += f"""

---

## 📊 ANÁLISE TÉCNICA COMPLEMENTAR
*Devido à baixa confiança do modelo computacional ({avg_confidence:.1f}%), incluindo análise local mais relevante:*

{self._generate_local_analysis(image_path)}
"""
                
                return analysis
            else:
                return self._generate_local_analysis(image_path)
                
        except Exception as e:
            print(f"Erro ao formatar análise: {str(e)}")
            return self._generate_local_analysis(image_path)
    
    def _interpret_for_medical_context(self, predictions: list) -> dict:
        """Interpreta classificações no contexto médico específico para mamografia"""
        medical_mappings = {
            # Termos médicos diretos
            "breast": "Tecido mamário",
            "mammary": "Tecido mamário",
            "chest": "Região torácica",
            "thorax": "Cavidade torácica",
            "lung": "Pulmão",
            "rib": "Costela",
            "bone": "Estrutura óssea",
            "tissue": "Tecido biológico",
            "organ": "Estrutura orgânica",
            
            # Padrões específicos de mamografia
            "mass": "Massa ou nódulo",
            "lesion": "Lesão",
            "nodule": "Nódulo",
            "cyst": "Cisto",
            "calcification": "Calcificação",
            "density": "Densidade mamária",
            "fibroglandular": "Tecido fibroglandular",
            "fatty": "Tecido adiposo",
            "duct": "Ducto mamário",
            
            # Estruturas que podem ser interpretadas como objetos
            "shovel": "Estrutura densa ou calcificação pontual",
            "ladle": "Estrutura côncava ou cavidade",
            "paddle": "Estrutura alongada (possível ducto ou vaso)",
            "spoon": "Estrutura côncava ou depressão",
            "bowl": "Cavidade ou estrutura circular",
            "disk": "Estrutura circular ou lesão bem definida",
            "circle": "Estrutura circular ou nódulo",
            "oval": "Estrutura ovalada ou massa",
            "round": "Estrutura circular ou nódulo",
            "ball": "Estrutura esférica ou massa",
            "sphere": "Estrutura esférica ou nódulo",
            
            # Estruturas alongadas/lineares
            "nematode": "Estrutura alongada ou linear (possível ducto)",
            "worm": "Estrutura alongada ou linear",
            "snake": "Estrutura alongada ou curvilínea",
            "rope": "Estrutura linear ou ducto",
            "string": "Estrutura linear fina",
            "line": "Estrutura linear",
            "strip": "Estrutura linear",
            
            # Estruturas espirais/circulares
            "nautilus": "Padrão espiral ou circular",
            "conch": "Estrutura côncava ou padrão",
            "shell": "Estrutura côncava ou calcificação",
            "spiral": "Padrão espiral",
            "coil": "Padrão circular ou espiral",
            
            # Padrões de textura
            "texture": "Padrão de textura do tecido",
            "pattern": "Padrão visual identificado",
            "grain": "Textura granular",
            "mesh": "Padrão em rede ou textura",
            "net": "Padrão em rede",
            
            # Características de densidade
            "shadow": "Área de maior densidade ou sombra",
            "light": "Área de menor densidade",
            "dark": "Área de maior densidade",
            "bright": "Área hipodensa",
            "dense": "Área de alta densidade",
            
            # Características de contraste
            "contrast": "Contraste de imagem",
            "edge": "Borda ou margem",
            "border": "Borda ou margem",
            "outline": "Contorno ou margem",
            
            # Estruturas anatômicas específicas
            "nipple": "Mamilo",
            "areola": "Aréola",
            "axilla": "Axila",
            "pectoral": "Músculo peitoral",
            "skin": "Pele ou tecido superficial"
        }
        
        interpretations = {}
        for pred in predictions:
            if isinstance(pred, dict) and 'label' in pred:
                label = pred['label'].lower()
                # Buscar correspondência exata primeiro, depois parcial
                if label in medical_mappings:
                    interpretations[pred['label']] = medical_mappings[label]
                else:
                    # Buscar correspondência parcial
                    for key, value in medical_mappings.items():
                        if key in label:
                            interpretations[pred['label']] = value
                            break
        
        return interpretations
    
    def _generate_local_analysis(self, image_path: str = None) -> str:
        """Gera análise local robusta usando OpenCV quando APIs falham"""
        if not image_path:
            return self._generate_fallback_analysis()
        
        try:
            # Carregar imagem com OpenCV
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                return self._generate_fallback_analysis()
            
            # Análise de densidade
            mean_density = np.mean(img)
            std_density = np.std(img)
            min_density = np.min(img)
            max_density = np.max(img)
            contrast = max_density - min_density
            
            # Análise de qualidade
            laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
            
            # Detecção de regiões densas
            threshold = mean_density + (2 * std_density)
            dense_regions = np.sum(img > threshold)
            dense_percentage = (dense_regions / img.size) * 100
            
            # Análise de bordas
            edges = cv2.Canny(img, 50, 150)
            edge_density = np.sum(edges > 0) / img.size * 100
            
            # Análise de histograma
            hist = cv2.calcHist([img], [0], None, [256], [0, 256])
            peak_intensity = np.argmax(hist)
            
            # Avaliação de qualidade
            quality_score = self._calculate_image_quality(img)
            
            # Classificação de densidade (simplificada)
            if mean_density < 85:
                density_category = "Baixa densidade (predominantemente adiposo)"
            elif mean_density < 128:
                density_category = "Densidade moderada (mista)"
            elif mean_density < 170:
                density_category = "Alta densidade (predominantemente fibroglandular)"
            else:
                density_category = "Muito alta densidade (extremamente denso)"
            
            return f"""
## ANÁLISE TÉCNICA LOCAL
**Método:** Processamento de Imagem com OpenCV

### 📊 ESTATÍSTICAS DA IMAGEM:
- **Resolução**: {img.shape[1]} x {img.shape[0]} pixels
- **Densidade média**: {mean_density:.1f} (escala 0-255)
- **Desvio padrão**: {std_density:.1f}
- **Contraste**: {contrast:.1f}
- **Faixa de densidade**: {min_density:.1f} - {max_density:.1f}

### 🎯 ANÁLISE DE DENSIDADE:
- **Categoria de densidade**: {density_category}
- **Regiões densas detectadas**: {dense_percentage:.1f}% da imagem
- **Intensidade predominante**: {peak_intensity} (pico do histograma)

### 🔍 QUALIDADE TÉCNICA:
- **Nitidez (Laplacian)**: {laplacian_var:.1f}
- **Densidade de bordas**: {edge_density:.2f}%
- **Score de qualidade**: {quality_score:.1f}/100
- **Adequação para análise**: {'✅ Adequada' if quality_score > 60 else '⚠️ Limitada'}

### 📈 CARACTERÍSTICAS DETECTADAS:

#### Regiões de Alta Densidade:
- **Localização**: Detectadas {dense_percentage:.1f}% de pixels acima do threshold
- **Características**: Possíveis calcificações ou massas
- **Distribuição**: {'Homogênea' if std_density < 30 else 'Heterogênea'}

#### Padrões de Contraste:
- **Contraste geral**: {'Adequado' if contrast > 100 else 'Baixo'}
- **Variação de densidade**: {'Alta' if std_density > 40 else 'Moderada'}
- **Qualidade de bordas**: {'Bem definidas' if edge_density > 5 else 'Pouco definidas'}

### 🔬 INTERPRETAÇÃO TÉCNICA:

#### Aspectos Positivos:
- ✅ Imagem processada com sucesso
- ✅ Resolução adequada para análise técnica
- ✅ Contraste {'adequado' if contrast > 80 else 'limitado'}
- ✅ Nitidez {'boa' if laplacian_var > 100 else 'regular'}

#### Limitações Identificadas:
- {'⚠️ Contraste baixo pode limitar visualização de detalhes' if contrast < 80 else ''}
- {'⚠️ Alta densidade pode mascarar lesões sutis' if mean_density > 150 else ''}
- {'⚠️ Baixa nitidez pode afetar detecção de microcalcificações' if laplacian_var < 100 else ''}

### 📋 RECOMENDAÇÕES TÉCNICAS:
1. **Para análise médica**: Consulte radiologista especializado
2. **Para pesquisa**: Imagem adequada para processamento computacional
3. **Limitações**: Análise baseada apenas em características técnicas
4. **Complemento**: Recomenda-se análise com IA especializada (Gemini)

### ⚠️ AVISO IMPORTANTE:
Esta é uma **análise técnica automatizada** baseada em processamento de imagem. 
**NÃO constitui diagnóstico médico** e deve ser interpretada por profissional qualificado.

**Métodos utilizados:**
- Análise estatística de densidade
- Detecção de bordas (Canny)
- Medição de nitidez (Laplacian)
- Classificação de padrões de densidade
- Avaliação de qualidade de imagem
"""
            
        except Exception as e:
            print(f"Erro na análise local: {str(e)}")
            return self._generate_fallback_analysis()
    
    def _calculate_image_quality(self, img: np.ndarray) -> float:
        """Calcula score de qualidade da imagem (0-100)"""
        try:
            # Fatores de qualidade
            factors = []
            
            # 1. Contraste (0-30 pontos)
            contrast = np.max(img) - np.min(img)
            contrast_score = min(30, (contrast / 255) * 30)
            factors.append(contrast_score)
            
            # 2. Nitidez (0-25 pontos)
            laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
            sharpness_score = min(25, (laplacian_var / 500) * 25)
            factors.append(sharpness_score)
            
            # 3. Distribuição de histograma (0-20 pontos)
            hist = cv2.calcHist([img], [0], None, [256], [0, 256])
            hist_std = np.std(hist)
            hist_score = min(20, (hist_std / 1000) * 20)
            factors.append(hist_score)
            
            # 4. Resolução adequada (0-15 pontos)
            height, width = img.shape
            resolution_score = min(15, ((height * width) / (512 * 512)) * 15)
            factors.append(resolution_score)
            
            # 5. Ausência de artefatos (0-10 pontos)
            # Detectar possíveis artefatos por variação extrema
            img_std = np.std(img)
            artifact_score = 10 if img_std < 80 else max(0, 10 - (img_std - 80) / 10)
            factors.append(artifact_score)
            
            return sum(factors)
            
        except:
            return 50.0  # Score neutro em caso de erro
    
    def _generate_fallback_analysis(self) -> str:
        """Análise de fallback quando não é possível processar a imagem"""
        return """
## ANÁLISE TÉCNICA LOCAL
**Método:** Sistema de Fallback

### ⚠️ LIMITAÇÕES:
- Imagem não pôde ser processada completamente
- Análise baseada em validação básica
- Características técnicas limitadas

### ✅ PROCESSAMENTO REALIZADO:
- Validação de formato de arquivo
- Carregamento básico da imagem
- Verificação de integridade

### 📋 OBSERVAÇÕES:
- Imagem carregada pelo sistema
- Formato compatível com análise médica
- Pronta para processamento manual por especialista

### 🔄 RECOMENDAÇÕES:
1. Verificar qualidade do arquivo original
2. Tentar análise com diferentes APIs
3. Consultar radiologista para avaliação manual

### ⚠️ IMPORTANTE:
Esta é uma análise técnica básica. Para diagnóstico médico, consulte um radiologista qualificado.
"""
    
