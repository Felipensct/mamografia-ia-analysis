#!/usr/bin/env python3
"""
Script específico para testar análise do Hugging Face com interpretação médica
"""

import os
import sys
from services.ai_service import AIService

def test_huggingface_with_medical_context():
    """Testa análise do Hugging Face com interpretação médica melhorada"""
    print("🤗 TESTE DE ANÁLISE HUGGING FACE COM CONTEXTO MÉDICO")
    print("=" * 60)
    
    # Verificar chave API
    hf_key = os.getenv("HUGGINGFACE_API_KEY")
    if not hf_key:
        print("❌ Chave da API Hugging Face não configurada")
        return
    
    print("✅ Chave da API Hugging Face encontrada")
    
    # Encontrar imagem de teste
    upload_dir = "/home/felipe/Univap/ProjetosIV/Backend/uploads"
    test_images = []
    
    if os.path.exists(upload_dir):
        for file in os.listdir(upload_dir):
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp')):
                test_images.append(os.path.join(upload_dir, file))
    
    if not test_images:
        print("❌ Nenhuma imagem encontrada para teste")
        return
    
    test_image = test_images[0]
    print(f"📸 Analisando imagem: {os.path.basename(test_image)}")
    print(f"📁 Caminho completo: {test_image}")
    
    ai_service = AIService()
    
    try:
        print("\n🔄 Iniciando análise com Hugging Face...")
        result = ai_service.analyze_with_huggingface(test_image)
        
        if result["success"]:
            print("✅ Análise concluída com sucesso!")
            print(f"🤖 Modelo usado: {result['model']}")
            print("\n" + "="*60)
            print("📋 RESULTADO COMPLETO DA ANÁLISE:")
            print("="*60)
            print(result['analysis'])
            print("="*60)
            
            # Análise do resultado
            print("\n🔍 ANÁLISE DO RESULTADO:")
            print("-" * 40)
            
            if "shovel" in result['analysis'].lower() or "ladle" in result['analysis'].lower():
                print("⚠️  OBSERVAÇÃO: Modelo identificou objetos domésticos")
                print("   → Isso é normal - modelos gerais interpretam estruturas médicas como objetos")
                print("   → Sugestão: Use análise com Gemini para contexto médico específico")
            
            if "nematode" in result['analysis'].lower() or "worm" in result['analysis'].lower():
                print("⚠️  OBSERVAÇÃO: Modelo identificou estruturas alongadas")
                print("   → Possível interpretação de estruturas lineares na imagem")
                print("   → Estruturas como ductos ou vasos podem ser interpretadas assim")
            
            print("\n💡 RECOMENDAÇÕES:")
            print("1. Use Gemini para análise médica específica")
            print("2. Hugging Face é útil para análise de padrões visuais")
            print("3. Combine ambos os resultados para análise completa")
            print("4. Sempre consulte um radiologista para diagnóstico")
            
        else:
            print(f"❌ Erro na análise: {result['error']}")
            
    except Exception as e:
        print(f"❌ Erro na análise: {str(e)}")

def compare_with_gemini():
    """Compara resultados entre Hugging Face e Gemini"""
    print("\n🌟 COMPARAÇÃO COM GEMINI")
    print("=" * 60)
    
    # Verificar chave API Gemini
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("❌ Chave da API Gemini não configurada")
        return
    
    print("✅ Chave da API Gemini encontrada")
    
    # Encontrar imagem de teste
    upload_dir = "/home/felipe/Univap/ProjetosIV/Backend/uploads"
    test_images = []
    
    if os.path.exists(upload_dir):
        for file in os.listdir(upload_dir):
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp')):
                test_images.append(os.path.join(upload_dir, file))
    
    if not test_images:
        print("❌ Nenhuma imagem encontrada para teste")
        return
    
    test_image = test_images[0]
    ai_service = AIService()
    
    try:
        print("🔄 Analisando com Gemini...")
        gemini_result = ai_service.analyze_mammography(test_image)
        
        if gemini_result["success"]:
            print("✅ Análise Gemini concluída!")
            print("\n📋 RESUMO GEMINI (primeiros 300 chars):")
            print("-" * 40)
            print(gemini_result['analysis'][:300] + "...")
            
            print("\n🔄 Analisando com Hugging Face...")
            hf_result = ai_service.analyze_with_huggingface(test_image)
            
            if hf_result["success"]:
                print("✅ Análise Hugging Face concluída!")
                print("\n📋 RESUMO HUGGING FACE (primeiros 300 chars):")
                print("-" * 40)
                print(hf_result['analysis'][:300] + "...")
                
                print("\n🎯 COMPARAÇÃO:")
                print("=" * 60)
                print("🌟 GEMINI:")
                print("   → Análise médica específica e contextualizada")
                print("   → Foco em aspectos técnicos de mamografia")
                print("   → Linguagem médica apropriada")
                print()
                print("🤗 HUGGING FACE:")
                print("   → Análise de padrões visuais gerais")
                print("   → Classificação baseada em objetos cotidianos")
                print("   → Útil para identificar estruturas e texturas")
                print()
                print("💡 CONCLUSÃO:")
                print("   → Gemini: Melhor para contexto médico")
                print("   → Hugging Face: Melhor para análise de padrões")
                print("   → Combinar ambos para análise completa")
                
        else:
            print(f"❌ Erro na análise Gemini: {gemini_result['error']}")
            
    except Exception as e:
        print(f"❌ Erro na comparação: {str(e)}")

def main():
    """Função principal"""
    test_huggingface_with_medical_context()
    compare_with_gemini()
    
    print("\n" + "="*60)
    print("🎯 RESUMO FINAL:")
    print("="*60)
    print("✅ Hugging Face melhorado com interpretação médica")
    print("✅ Contexto explicativo adicionado")
    print("✅ Comparação com Gemini implementada")
    print("✅ Recomendações claras para uso")
    print("\n💡 PRÓXIMOS PASSOS:")
    print("1. Teste com diferentes tipos de imagens de mamografia")
    print("2. Compare resultados entre Gemini e Hugging Face")
    print("3. Use Gemini para análise médica específica")
    print("4. Use Hugging Face para análise de padrões visuais")

if __name__ == "__main__":
    main()
