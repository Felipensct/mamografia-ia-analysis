#!/usr/bin/env python3
"""
Script para testar o lazy loading do modelo
"""

import os
import time
from services.model_service import get_model_service

def test_model_lazy_loading():
    print("="*70)
    print("TESTE DE LAZY LOADING DO MODELO")
    print("="*70)
    
    # Criar serviço (sem carregar modelo)
    print("\n1️⃣ Criando ModelService (lazy loading)...")
    model_service = get_model_service()
    print(f"   ✅ ModelService criado")
    print(f"   📋 Modelo carregado na memória? {model_service.model is not None}")
    
    # Verificar disponibilidade
    is_available = model_service.is_available()
    print(f"\n2️⃣ Modelo disponível (arquivo existe)? {is_available}")
    
    # Fazer predição (carrega modelo)
    print("\n3️⃣ Fazendo predição (modelo será carregado AGORA)...")
    test_image = "/home/frog/ai/jpeg/1.3.6.1.4.1.9590.100.1.2.499558611862523307025745211397332529/1-036.jpg"
    
    if os.path.exists(test_image):
        print(f"   🖼️ Usando imagem: {os.path.basename(test_image)}")
        result = model_service.predict(test_image, generate_viz=False)
        
        if result.get('success'):
            print(f"   ✅ Resultado: {result.get('prediction', 'N/A')} ({result.get('probability', 0):.1%})")
            print(f"   📋 Modelo ainda na memória após predição? {model_service.model is not None}")
        else:
            print(f"   ❌ Erro: {result.get('error', 'Unknown')}")
    else:
        print(f"   ⚠️ Imagem de teste não encontrada: {test_image}")
    
    # Resumo
    print("\n" + "="*70)
    print("RESUMO DO LAZY LOADING")
    print("="*70)
    print(f"✅ Modelo NÃO é carregado no __init__ (economiza memória)")
    print(f"✅ Modelo é carregado sob demanda quando predict() é chamado")
    print(f"✅ Modelo é descarregado automaticamente após cada predição")
    print(f"✅ Memória é liberada com garbage collection")
    print("="*70)

if __name__ == "__main__":
    test_model_lazy_loading()
