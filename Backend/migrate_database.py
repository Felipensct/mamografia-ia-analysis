#!/usr/bin/env python3
"""
Script de Migração do Banco de Dados - Mamografia IA
Adiciona colunas 'info' e 'image_hash' se não existirem
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
        
        # Verificar colunas existentes
        cursor.execute("PRAGMA table_info(analyses)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrations_needed = []
        
        # Verificar e adicionar coluna 'info'
        if 'info' not in columns:
            migrations_needed.append('info')
        
        # Verificar e adicionar coluna 'image_hash'
        if 'image_hash' not in columns:
            migrations_needed.append('image_hash')
        
        if not migrations_needed:
            print("✅ Todas as colunas já existem. Migração não necessária.")
            return True
        
        print(f"⚠️  Colunas faltando: {', '.join(migrations_needed)}. Executando migração...")
        
        # Adicionar coluna info se necessário
        if 'info' in migrations_needed:
            cursor.execute("ALTER TABLE analyses ADD COLUMN info TEXT")
            print("✅ Coluna 'info' adicionada.")
        
        # Adicionar coluna image_hash se necessário
        if 'image_hash' in migrations_needed:
            cursor.execute("ALTER TABLE analyses ADD COLUMN image_hash VARCHAR(32)")
            # Criar índice para melhor performance nas buscas de cache
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_image_hash ON analyses(image_hash)")
                print("✅ Coluna 'image_hash' adicionada com índice.")
            except Exception as e:
                print(f"⚠️  Coluna 'image_hash' adicionada, mas índice não criado: {str(e)}")
        
        conn.commit()
        
        print("✅ Migração concluída!")
        
        # Verificar se funcionou
        cursor.execute("PRAGMA table_info(analyses)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'info' in columns and 'image_hash' in columns:
            print("✅ Verificação: Todas as colunas criadas com sucesso!")
            return True
        else:
            print("❌ Erro: Algumas colunas não foram criadas!")
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
        
        # Verificar colunas necessárias
        column_names = [col[1] for col in columns]
        missing_columns = []
        
        if 'info' not in column_names:
            missing_columns.append('info')
        if 'image_hash' not in column_names:
            missing_columns.append('image_hash')
        
        if not missing_columns:
            print("✅ Status: Migração OK - Todas as colunas presentes")
        else:
            print(f"⚠️  Status: Migração necessária - Colunas ausentes: {', '.join(missing_columns)}")
            
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
