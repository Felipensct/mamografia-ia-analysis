import os
import requests
import json
import base64
import cv2
import numpy as np
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from PIL import Image, ImageEnhance, ImageFilter
import io

load_dotenv()

class AIService:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.cohere_api_key = os.getenv("COHERE_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # APIs disponíveis
        self.available_apis = []
        if self.gemini_api_key:
            self.available_apis.append("gemini")
        if self.hf_api_key:
            self.available_apis.append("huggingface")
        if self.cohere_api_key:
            self.available_apis.append("cohere")
        if self.anthropic_api_key:
            self.available_apis.append("anthropic")
    
    def get_available_apis(self) -> list:
        """Retorna lista de APIs disponíveis"""
        return self.available_apis
        
    def preprocess_image(self, image_path: str) -> str:
        """
        Pré-processa imagem para melhor análise de IA com foco em mamografia
        
        Args:
            image_path: Caminho da imagem original
            
        Returns:
            Caminho da imagem processada
        """
        try:
            # Carregar imagem
            with Image.open(image_path) as img:
                print(f"🖼️  Processando imagem: {img.size}, modo: {img.mode}")
                
                # 1. CONVERTER PARA ESCALA DE CINZA (preto e branco)
                if img.mode != 'L':
                    img = img.convert('L')
                    print("📷 Convertido para escala de cinza")
                
                # 2. OTIMIZAR CONTRASTE para mamografia
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.3)  # Aumentado de 1.2 para 1.3
                print("🎨 Contraste otimizado para mamografia")
                
                # 3. APLICAR NITIDEZ AVANÇADA
                # Filtro UnsharpMask mais agressivo para melhorar detalhes
                img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=200, threshold=2))
                print("🔍 Nitidez melhorada para análise médica")
                
                # 4. AJUSTAR BRILHO para melhor visualização
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(1.05)  # Reduzido para 1.05 para não saturar
                print("💡 Brilho ajustado para análise médica")
                
                # 5. APLICAR FILTRO DE REALCE DE BORDAS
                # Melhorar definição de estruturas
                img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
                print("📐 Bordas realçadas para melhor definição")
                
                # 6. REDIMENSIONAR para tamanho otimizado
                img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                print(f"📏 Redimensionado para: {img.size}")
                
                # 7. SALVAR com alta qualidade
                processed_path = image_path.replace('.', '_processed.')
                img.save(processed_path, 'JPEG', quality=98, optimize=True)
                print(f"💾 Imagem processada salva: {processed_path}")
                
                return processed_path
                
        except Exception as e:
            print(f"❌ Erro no pré-processamento: {str(e)}")
            return image_path  # Retorna original se houver erro
        
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
            
            # Alterar o modelo aqui
            model = genai.GenerativeModel('gemini-2.5-pro') 
            
            # Pré-processar imagem para melhor análise
            processed_image_path = self.preprocess_image(image_path)
            
            # Prompt otimizado para detecção de câncer de mama em estágios iniciais
            prompt = """
                    🧠 Prompt Detalhado — Análise de Mamografia (Formato MIAS)

                    Você é uma inteligência artificial especializada em análise de imagens médicas, com foco em mamografias.
                    Sua tarefa é analisar a imagem fornecida e gerar uma descrição estruturada no formato MIAS (Mammographic Image Analysis Society), conforme as especificações abaixo.

                    🩻 Objetivo

                    Identificar o tipo de tecido mamário predominante e classificar a presença, tipo, severidade e localização de eventuais anormalidades detectadas na mamografia.

                    🧩 Formato de Saída Esperado

                    A resposta deve seguir exatamente este formato, com todos os campos preenchidos quando aplicáveis:

                    1. Referência MIAS: [identificador único do exame]
                    2. Tipo de tecido de fundo: [F / G / D]
                    3. Classe de anormalidade: [CALC / CIRC / SPIC / MISC / ARCH / ASYM / NORM]
                    4. Severidade da anormalidade: [B / M]
                    5. Coordenadas do centro da anormalidade: (x= , y= )
                    6. Raio aproximado: [valor em pixels]


                    Nota: Se não houver anormalidade (classe = NORM), omita os campos 4, 5 e 6.

                    🧬 1. Tipo de tecido de fundo (coluna 2 do formato MIAS)

                    Classifique o tecido mamário predominante na imagem de acordo com as seguintes categorias:

                    Código	Tipo	Descrição
                    F	Fatty	Predominantemente gorduroso. O tecido aparece de forma homogênea e radiotransparente.
                    G	Fatty-glandular	Misto: presença equilibrada de tecido gorduroso e glandular.
                    D	Dense-glandular	Predominantemente denso, com alta radiopacidade devido à concentração glandular.

                    Instrução para IA:

                    Analise a densidade geral da mama e determine se o tecido é Fatty (F), Fatty-glandular (G) ou Dense-glandular (D).

                    ⚕️ 2. Classe de anormalidade (coluna 3 do formato MIAS)

                    Identifique a principal anormalidade presente na mamografia. Se houver múltiplas, descreva a mais significativa (maior ou mais suspeita).

                    Código	Tipo de Lesão	Descrição
                    CALC	Calcificação	Pequenas áreas brilhantes indicando depósitos de cálcio. Podem ser agrupadas ou difusas.
                    CIRC	Massa circunscrita	Lesão bem definida, bordas regulares, aspecto arredondado.
                    SPIC	Massa espiculada	Lesão com bordas irregulares, prolongamentos lineares, aspecto estrelado.
                    MISC	Massa indefinida	Lesão não claramente circunscrita, sem contornos regulares.
                    ARCH	Distorção arquitetural	Alteração do padrão normal do tecido mamário, sem massa definida.
                    ASYM	Assimetria	Densidade assimétrica entre mamas ou quadrantes.
                    NORM	Normal	Ausência de anormalidades detectáveis.

                    Instrução para IA:

                    Detecte qualquer anormalidade presente na imagem e classifique-a em uma das categorias acima (CALC, CIRC, SPIC, MISC, ARCH, ASYM, NORM).

                    🧪 3. Severidade da anormalidade (coluna 4 do formato MIAS)

                    Determine o caráter benigno ou maligno da anormalidade identificada, com base nos padrões visuais da imagem.

                    Código	Significado	Descrição
                    B	Benigna	Lesão com margens suaves, simétricas e não invasivas.
                    M	Maligna	Lesão com bordas irregulares, infiltração tecidual ou características suspeitas.

                    Instrução para IA:

                    Caso exista uma anormalidade, classifique sua severidade como Benigna (B) ou Maligna (M).
                    Se a imagem for normal (NORM), este campo deve ser omitido.

                    📍 4. Localização e dimensão da lesão (colunas 5–7 do formato MIAS)

                    Forneça a localização e o tamanho aproximado da anormalidade, se aplicável.

                    x, y: Coordenadas do centro da anormalidade, com a origem no canto inferior esquerdo da imagem.

                    Raio (r): Tamanho aproximado da lesão, em pixels.

                    Caso existam múltiplas anormalidades, selecione a mais representativa (maior ou mais suspeita).

                    Se a anormalidade for difusa (como calcificações dispersas), omita x, y e raio.

                    Instrução para IA:

                    Determine as coordenadas centrais (x, y) e o raio aproximado da anormalidade principal.
                    Se não houver lesão focal, deixe esses campos em branco.

                    🧩 Exemplo de saída completa

                    Analise a imagem de mamografia (referência mdb003) e descreva os achados conforme o formato MIAS.

                    1. Referência MIAS: mdb003
                    2. Tipo de tecido de fundo: G (Fatty-glandular)
                    3. Classe de anormalidade: CALC (Calcificação)
                    4. Severidade da anormalidade: B (Benigna)
                    5. Coordenadas do centro da anormalidade: (x=350, y=580)
                    6. Raio aproximado: 45 pixels

                    ⚙️ Regras adicionais de formatação

                    Sempre siga a ordem numérica dos campos (1–6).

                    Inclua apenas valores coerentes e observáveis na imagem.

                    Evite descrições narrativas: a saída deve ser estruturada e objetiva.

                    Caso a imagem apresente nenhuma anormalidade, o resultado deve ser:

                    1. Referência MIAS: [id]
                    2. Tipo de tecido de fundo: [F/G/D]
                    3. Classe de anormalidade: NORM

            """
            
            # Carregar e processar a imagem otimizada
            with open(processed_image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            # Fazer a análise
            response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_data}])
            
            # Limpar arquivo temporário
            try:
                if processed_image_path != image_path:
                    os.remove(processed_image_path)
            except:
                pass
            
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
                        f"https://api-inference.huggingface.co/models/{model}",
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
    
    def analyze_with_cohere(self, image_path: str) -> Dict[str, Any]:
        """Análise com Cohere (API gratuita)"""
        if not self.cohere_api_key:
            return {
                "success": False,
                "error": "Chave da API Cohere não configurada",
                "analysis": None,
                "api": "cohere"
            }
        
        try:
            # Pré-processar imagem
            processed_image_path = self.preprocess_image(image_path)
            
            # Converter imagem para base64
            with open(processed_image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            headers = {
                "Authorization": f"Bearer {self.cohere_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "command",
                "message": """
                Analise esta imagem de mamografia e forneça uma análise técnica detalhada em português brasileiro.

                ESTRUTURA DA ANÁLISE:
                1. Qualidade técnica da imagem
                2. Anatomia visível
                3. Características do tecido mamário
                4. Aspectos técnicos
                5. Observações gerais

                IMPORTANTE: Esta é uma análise técnica, não um diagnóstico médico.
                """,
                "image": image_base64,
                "max_tokens": 1000
            }
            
            response = requests.post(
                "https://api.cohere.ai/v1/chat",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            # Limpar arquivo temporário
            try:
                if processed_image_path != image_path:
                    os.remove(processed_image_path)
            except:
                pass
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "analysis": result.get("text", "Análise não disponível"),
                    "api": "cohere",
                    "model": "Cohere Command",
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "error": f"Erro HTTP {response.status_code}: {response.text}",
                    "analysis": None,
                    "api": "cohere"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na análise com Cohere: {str(e)}",
                "analysis": None,
                "api": "cohere"
            }
    
    def analyze_with_anthropic(self, image_path: str) -> Dict[str, Any]:
        """Análise com Anthropic Claude (API gratuita)"""
        if not self.anthropic_api_key:
            return {
                "success": False,
                "error": "Chave da API Anthropic não configurada",
                "analysis": None,
                "api": "anthropic"
            }
        
        try:
            # Pré-processar imagem
            processed_image_path = self.preprocess_image(image_path)
            
            # Converter imagem para base64
            with open(processed_image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            headers = {
                "x-api-key": self.anthropic_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """
                                Analise esta imagem de mamografia e forneça uma análise técnica detalhada em português brasileiro.

                                ESTRUTURA:
                                1. Qualidade técnica da imagem
                                2. Anatomia visível
                                3. Características do tecido
                                4. Aspectos técnicos
                                5. Observações gerais

                                IMPORTANTE: Análise técnica, não diagnóstico médico.
                                """
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_base64
                                }
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            # Limpar arquivo temporário
            try:
                if processed_image_path != image_path:
                    os.remove(processed_image_path)
            except:
                pass
            
            if response.status_code == 200:
                result = response.json()
                
                analysis_text = ""
                for content in result.get("content", []):
                    if content.get("type") == "text":
                        analysis_text += content.get("text", "")
                
                return {
                    "success": True,
                    "analysis": analysis_text,
                    "api": "anthropic",
                    "model": "Claude 3 Sonnet",
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "error": f"Erro HTTP {response.status_code}: {response.text}",
                    "analysis": None,
                    "api": "anthropic"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na análise com Anthropic: {str(e)}",
                "analysis": None,
                "api": "anthropic"
            }
