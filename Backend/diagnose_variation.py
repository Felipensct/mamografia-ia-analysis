#!/usr/bin/env python3
"""
Script de Diagnóstico - Variação nos Resultados
Analisa por que a mesma imagem gera resultados diferentes
"""

import os
import hashlib
import sys
from pathlib import Path
from PIL import Image
import numpy as np

def calculate_file_hash(file_path: str) -> str:
    """Calcula hash MD5 do arquivo"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def calculate_image_hash(image_path: str) -> str:
    """Calcula hash MD5 da imagem processada (como PIL salva)"""
    try:
        with Image.open(image_path) as img:
            # Converter para array numpy e calcular hash
            img_array = np.array(img)
            hash_md5 = hashlib.md5(img_array.tobytes())
            return hash_md5.hexdigest()
    except Exception as e:
        return f"ERRO: {str(e)}"

def preprocess_and_save(image_path: str, output_path: str) -> dict:
    """Simula o pré-processamento e retorna informações"""
    from PIL import Image, ImageEnhance, ImageFilter
    
    try:
        with Image.open(image_path) as img:
            original_size = img.size
            original_mode = img.mode
            
            is_pgm = image_path.lower().endswith('.pgm')
            
            # Simular processamento
            if is_pgm and img.mode in ['L', 'I', 'F']:
                pass  # Manter modo original
            elif img.mode != 'L':
                img = img.convert('L')
            
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.15)
            
            img = img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=150, threshold=3))
            
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.02)
            
            if not is_pgm:
                img = img.filter(ImageFilter.EDGE_ENHANCE)
            
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            final_size = img.size
            
            # Salvar
            img.save(output_path, 'JPEG', quality=98, optimize=False)
            
            return {
                "original_size": original_size,
                "original_mode": original_mode,
                "final_size": final_size,
                "final_mode": img.mode,
                "success": True
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def diagnose_image(image_path: str):
    """Diagnostica uma imagem específica"""
    print(f"\n{'='*60}")
    print(f"DIAGNÓSTICO: {image_path}")
    print(f"{'='*60}\n")
    
    if not os.path.exists(image_path):
        print(f"❌ Arquivo não encontrado: {image_path}")
        return
    
    # 1. Hash do arquivo original
    file_hash = calculate_file_hash(image_path)
    print(f"📄 Hash MD5 do arquivo original: {file_hash}")
    
    # 2. Informações da imagem original
    try:
        with Image.open(image_path) as img:
            print(f"📐 Dimensões originais: {img.size}")
            print(f"🎨 Modo original: {img.mode}")
            print(f"📊 Formato: {img.format}")
    except Exception as e:
        print(f"❌ Erro ao abrir imagem: {str(e)}")
        return
    
    # 3. Processar múltiplas vezes e comparar
    print(f"\n🔄 Processando imagem 3 vezes para verificar consistência...")
    
    processed_hashes = []
    for i in range(3):
        output_path = f"/tmp/test_processed_{i}.jpg"
        result = preprocess_and_save(image_path, output_path)
        
        if result["success"]:
            processed_hash = calculate_file_hash(output_path)
            processed_hashes.append(processed_hash)
            print(f"  Processamento {i+1}: Hash = {processed_hash[:16]}... | Tamanho = {result['final_size']}")
            
            # Limpar arquivo temporário
            try:
                os.remove(output_path)
            except:
                pass
        else:
            print(f"  ❌ Erro no processamento {i+1}: {result.get('error', 'Desconhecido')}")
    
    # 4. Verificar se os hashes são iguais
    if len(processed_hashes) == 3:
        if processed_hashes[0] == processed_hashes[1] == processed_hashes[2]:
            print(f"\n✅ PRÉ-PROCESSAMENTO É DETERMINÍSTICO")
            print(f"   Todos os 3 processamentos geraram o mesmo hash")
        else:
            print(f"\n❌ PRÉ-PROCESSAMENTO NÃO É DETERMINÍSTICO")
            print(f"   Hash 1: {processed_hashes[0][:16]}...")
            print(f"   Hash 2: {processed_hashes[1][:16]}...")
            print(f"   Hash 3: {processed_hashes[2][:16]}...")
            print(f"\n   ⚠️  Isso pode causar variação nos resultados!")
    
    # 5. Verificar se há arquivos processados existentes
    base_name = Path(image_path).stem
    upload_dir = Path(__file__).parent / "uploads"
    processed_files = list(upload_dir.glob(f"*{base_name}*_processed.*"))
    
    if processed_files:
        print(f"\n📁 Arquivos processados encontrados:")
        for pf in processed_files:
            pf_hash = calculate_file_hash(str(pf))
            print(f"   {pf.name}: Hash = {pf_hash[:16]}...")
    else:
        print(f"\n📁 Nenhum arquivo processado encontrado no diretório uploads")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python diagnose_variation.py <caminho_da_imagem>")
        print("\nExemplo:")
        print("  python diagnose_variation.py /home/felipenascimento/Imagens/archive/all-mias/mdb001.pgm")
        sys.exit(1)
    
    image_path = sys.argv[1]
    diagnose_image(image_path)


