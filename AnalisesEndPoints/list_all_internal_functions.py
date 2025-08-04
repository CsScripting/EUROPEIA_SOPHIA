#!/usr/bin/env python3
"""
Script para descobrir TODAS as funções INTERNAS do Sophia Plus
Usando a operação GetFunctionsList do SOAP
Autor: Paulo - Professional Services
"""

from zeep import Client
import xml.etree.ElementTree as ET
from datetime import datetime
import logging
import os

# --- Setup Logging ---
log_dir = "LOGS"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file_name = f"all_internal_functions_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"
log_file_path = os.path.join(log_dir, log_file_name)

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(message)s'))

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Write Markdown header
with open(log_file_path, 'w', encoding='utf-8') as f:
    f.write(f"# 🔍 Todas as Funções Internas do Sophia Plus\n")
    f.write(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
    f.write(f"**Autor:** Paulo - Professional Services  \n")
    f.write(f"**Método:** Operação GetFunctionsList do SOAP  \n")
    f.write(f"**Objetivo:** Descobrir TODAS as funções internas disponíveis\n\n")

def get_all_internal_functions():
    """Usa GetFunctionsList para descobrir todas as funções internas"""
    wsdl_url = "https://elpusonlinelisboaqa.ipam.pt/WebSAPI/websapi.asmx?WSDL"
    
    try:
        logger.info("🔍 USANDO GetFunctionsList para descobrir funções internas...")
        
        client = Client(wsdl_url)
        
        # Teste com diferentes formatos
        formats_to_try = [
            {'FormatoInput': 'JSON', 'FormatoOutput': 'JSON'},
            {'FormatoInput': 'XML', 'FormatoOutput': 'XML'},
            {'FormatoInput': '', 'FormatoOutput': ''}
        ]
        
        for i, params in enumerate(formats_to_try, 1):
            logger.info(f"   🔄 Tentativa {i}: {params}")
            
            try:
                response = client.service.GetFunctionsList(**params)
                
                if response:
                    logger.info(f"   ✅ Resposta recebida ({len(response)} caracteres)")
                    logger.info("   📝 Resposta completa:")
                    logger.info(f"{response}")
                    return response
                else:
                    logger.info("   ❌ Sem resposta")
                    
            except Exception as e:
                logger.info(f"   ❌ Erro: {str(e)}")
        
        return None
        
    except Exception as e:
        logger.error(f"❌ ERRO GERAL: {str(e)}")
        return None

def main():
    """Função principal"""
    
    logger.info("🎯 DESCOBERTA COMPLETA DE FUNÇÕES INTERNAS")
    logger.info("👤 Paulo - Professional Services")
    
    # Descobrir todas as funções internas
    response = get_all_internal_functions()
    
    if response:
        logger.info("✅ Conseguimos obter resposta do GetFunctionsList!")
        
        # Write response to file
        with open(log_file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n## 📋 Resposta do GetFunctionsList\n\n")
            f.write(f"```xml\n{response}\n```\n")
    else:
        logger.warning("⚠️ Não foi possível obter lista de funções")
    
    logger.info(f"📄 Log salvo em: {log_file_path}")

if __name__ == "__main__":
    main() 