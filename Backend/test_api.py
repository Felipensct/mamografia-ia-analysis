#!/usr/bin/env python3
"""
Script de teste para a API de Análise de Mamografias
Testa todos os endpoints principais da aplicação
"""

import requests
import json
import os
from pathlib import Path

# Configurações
BASE_URL = "http://localhost:8000"
TEST_IMAGE_PATH = "test_image.jpg"  # Você pode usar qualquer imagem para teste

def test_health():
    """Testa o endpoint de saúde da API"""
    print("🔍 Testando endpoint de saúde...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API está funcionando!")
            print(f"   Status: {response.json()['status']}")
            return True
        else:
            print(f"❌ Erro na API: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def test_upload():
    """Testa o upload de uma imagem"""
    print("\n📤 Testando upload de imagem...")
    
    # Criar uma imagem de teste simples se não existir
    if not os.path.exists(TEST_IMAGE_PATH):
        print("   Criando imagem de teste...")
        from PIL import Image
        import io
        
        # Criar uma imagem simples de 100x100 pixels
        img = Image.new('RGB', (100, 100), color='white')
        img.save(TEST_IMAGE_PATH, 'JPEG')
        print(f"   Imagem de teste criada: {TEST_IMAGE_PATH}")
    
    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'file': (TEST_IMAGE_PATH, f, 'image/jpeg')}
            response = requests.post(f"{BASE_URL}/api/v1/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Upload realizado com sucesso!")
            print(f"   ID da análise: {data['analysis_id']}")
            print(f"   Nome do arquivo: {data['filename']}")
            return data['analysis_id']
        else:
            print(f"❌ Erro no upload: {response.status_code}")
            print(f"   Detalhes: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro no upload: {e}")
        return None

def test_list_analyses():
    """Testa a listagem de análises"""
    print("\n📋 Testando listagem de análises...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/analyses")
        if response.status_code == 200:
            data = response.json()
            print("✅ Listagem realizada com sucesso!")
            print(f"   Total de análises: {data['count']}")
            for analysis in data['analyses']:
                print(f"   - ID: {analysis['id']}, Status: {analysis['status']}")
            return True
        else:
            print(f"❌ Erro na listagem: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro na listagem: {e}")
        return False

def test_analysis(analysis_id):
    """Testa a análise de uma imagem"""
    print(f"\n🤖 Testando análise da imagem ID {analysis_id}...")
    try:
        response = requests.post(f"{BASE_URL}/api/v1/analyze/{analysis_id}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Análise realizada com sucesso!")
            print(f"   Status: {data['status']}")
            print(f"   Modelo: {data.get('model', 'N/A')}")
            if 'analysis' in data:
                print(f"   Resultado: {data['analysis'][:200]}...")
            return True
        else:
            print(f"❌ Erro na análise: {response.status_code}")
            print(f"   Detalhes: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        return False

def test_get_analysis(analysis_id):
    """Testa a obtenção de detalhes de uma análise"""
    print(f"\n🔍 Testando obtenção de detalhes da análise ID {analysis_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/analysis/{analysis_id}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Detalhes obtidos com sucesso!")
            print(f"   Status: {data['status']}")
            print(f"   Processado: {data.get('is_processed', False)}")
            if data.get('results', {}).get('gemini'):
                print(f"   Análise Gemini: {data['results']['gemini'][:200]}...")
            return True
        else:
            print(f"❌ Erro ao obter detalhes: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao obter detalhes: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes da API de Análise de Mamografias")
    print("=" * 60)
    
    # Verificar se a API está rodando
    if not test_health():
        print("\n❌ API não está funcionando. Execute 'python3 app.py' primeiro.")
        return
    
    # Testar upload
    analysis_id = test_upload()
    if not analysis_id:
        print("\n❌ Falha no upload. Testes interrompidos.")
        return
    
    # Testar listagem
    test_list_analyses()
    
    # Testar análise (pode falhar se não tiver chaves de API configuradas)
    test_analysis(analysis_id)
    
    # Testar obtenção de detalhes
    test_get_analysis(analysis_id)
    
    print("\n" + "=" * 60)
    print("🎉 Testes concluídos!")
    print("\n💡 Dicas:")
    print("   - Para análise com IA, configure o arquivo .env com suas chaves de API")
    print("   - Acesse http://localhost:8000/docs para interface interativa")
    print("   - Use 'python3 app.py' para iniciar a API")

if __name__ == "__main__":
    main()
