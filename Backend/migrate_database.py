#!/usr/bin/env python3
"""
Script de Migração do Banco de Dados - Mamografia IA
Adiciona coluna 'info' se não existir
"""

import sqlite3
import os
from pathlib import Path

def migrate_database():
    """Executa migração do banco de dados"""
    
    # Caminho do banco
    db_path = Path(__file__).parent / "mamografia_analysis.db"
    
    if not db_path.exists():
        print("📁 Banco de dados não encontrado. Será criado automaticamente ao iniciar a aplicação.")
        return True
    
    print(f"🔍 Verificando banco: {db_path}")
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Verificar se a coluna 'info' já existe
        cursor.execute("PRAGMA table_info(analyses)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'info' in columns:
            print("✅ Coluna 'info' já existe. Migração não necessária.")
            return True
        
        print("⚠️  Coluna 'info' não encontrada. Executando migração...")
        
        # Adicionar coluna info
        cursor.execute("ALTER TABLE analyses ADD COLUMN info TEXT")
        conn.commit()
        
        print("✅ Migração concluída! Coluna 'info' adicionada.")
        
        # Verificar se funcionou
        cursor.execute("PRAGMA table_info(analyses)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'info' in columns:
            print("✅ Verificação: Coluna 'info' criada com sucesso!")
            return True
        else:
            print("❌ Erro: Coluna 'info' não foi criada!")
            return False
            
    except Exception as e:
        print(f"❌ Erro na migração: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def check_database_status():
    """Verifica status do banco de dados"""
    
    db_path = Path(__file__).parent / "mamografia_analysis.db"
    
    if not db_path.exists():
        print("📁 Status: Banco não existe (será criado automaticamente)")
        return
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(analyses)")
        columns = cursor.fetchall()
        
        print("📊 Estrutura da tabela 'analyses':")
        for column in columns:
            print(f"  - {column[1]} ({column[2]})")
        
        # Verificar se tem coluna info
        column_names = [col[1] for col in columns]
        if 'info' in column_names:
            print("✅ Status: Migração OK - Coluna 'info' presente")
        else:
            print("⚠️  Status: Migração necessária - Coluna 'info' ausente")
            
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        check_database_status()
    else:
        print("🔄 Iniciando migração do banco de dados...")
        success = migrate_database()
        
        if success:
            print("🎉 Migração concluída com sucesso!")
            print("💡 Você pode agora executar a aplicação normalmente.")
        else:
            print("❌ Falha na migração. Verifique os logs acima.")
            sys.exit(1)
