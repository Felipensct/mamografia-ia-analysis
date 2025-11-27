#!/bin/bash

echo "🔧 Instalando suporte DICOM para análise de mamografias"
echo "=================================================="

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    echo "📦 Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Instalar pydicom
echo "📥 Instalando biblioteca pydicom..."
pip install pydicom

# Verificar instalação
echo "🔍 Verificando instalação..."
python -c "import pydicom; print('✅ pydicom instalado com sucesso')"

echo ""
echo "🎉 Suporte DICOM instalado com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo "1. Execute: python app.py"
echo "2. Em outro terminal, execute: python test_dicom_support.py"
echo "3. Coloque um arquivo .dcm do dataset CBIS-DDSM na pasta Backend/"
echo ""
echo "💡 O projeto agora suporta:"
echo "   - Arquivos DICOM (.dcm) do dataset CBIS-DDSM"
echo "   - Conversão automática para formato otimizado"
echo "   - Preservação de metadados DICOM"
echo "   - Análise com IA especializada"
