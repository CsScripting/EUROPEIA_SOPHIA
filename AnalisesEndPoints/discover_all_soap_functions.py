#!/usr/bin/env python3
"""
Script para descobrir TODAS as funções disponíveis no endpoint SOAP
Autor: Paulo - Professional Services
Objetivo: Enumerar todas as operações disponíveis no serviço SOAP Sophia Plus
"""

from zeep import Client
from datetime import datetime
import logging
import os

# --- Setup Logging ---
log_dir = "LOGS"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Generate timestamped log file
log_file_name = f"all_soap_functions_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"
log_file_path = os.path.join(log_dir, log_file_name)

# Custom Markdown formatter
class MarkdownFormatter(logging.Formatter):
    def format(self, record):
        msg = record.getMessage()
        
        if "🎯" in msg:
            return f"# {msg}"
        elif "👤" in msg:
            return f"**{msg}**\n"
        elif "📊" in msg and "DESCOBERTA" in msg:
            return f"\n## {msg}"
        elif "🔍" in msg and "WSDL" in msg:
            return f"\n### {msg}"
        elif msg.startswith("✅"):
            return f"**{msg}**"
        elif msg.startswith("   🔹"):
            return f"- {msg.replace('   🔹 ', '')}"
        elif msg.startswith("📋"):
            return f"\n### {msg}"
        elif "Total de operações" in msg:
            return f"\n**{msg}**"
        elif msg.startswith("   "):
            return f"  {msg.strip()}"
        else:
            return msg

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
file_handler.setFormatter(MarkdownFormatter())

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(message)s'))

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Write Markdown header
with open(log_file_path, 'w', encoding='utf-8') as f:
    f.write(f"# 🔍 Descoberta Completa - Todas as Funções SOAP\n")
    f.write(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
    f.write(f"**Autor:** Paulo - Professional Services  \n")
    f.write(f"**Objetivo:** Enumerar TODAS as funções disponíveis no endpoint SOAP\n")
    f.write(f"**Endpoint:** https://elpusonlinelisboaqa.ipam.pt/WebSAPI/\n\n")

def discover_all_soap_operations():
    """Descobre todas as operações SOAP disponíveis no WSDL"""
    wsdl_url = "https://elpusonlinelisboaqa.ipam.pt/WebSAPI/websapi.asmx?WSDL"
    
    try:
        logger.info("🔍 ANALISANDO WSDL...")
        logger.info(f"   URL: {wsdl_url}")
        
        # Criar cliente SOAP
        client = Client(wsdl_url)
        
        # Obter informações do serviço
        service = client.service
        
        # Listar todas as operações
        operations = []
        
        logger.info("📊 DESCOBERTA DE OPERAÇÕES")
        
        # Iterar sobre todas as operações disponíveis
        for operation_name in dir(service):
            if not operation_name.startswith('_'):
                operations.append(operation_name)
        
        # Ordenar alfabeticamente
        operations.sort()
        
        logger.info(f"✅ Total de operações encontradas: {len(operations)}")
        
        logger.info("📋 LISTA COMPLETA DE OPERAÇÕES:")
        
        for i, operation in enumerate(operations, 1):
            logger.info(f"   🔹 {i:3d}. {operation}")
            
            # Tentar obter informações sobre a operação
            try:
                operation_obj = getattr(service, operation)
                # Algumas operações podem ter documentação
                if hasattr(operation_obj, '__doc__') and operation_obj.__doc__:
                    logger.info(f"      📝 {operation_obj.__doc__.strip()}")
            except:
                pass
        
        return operations
        
    except Exception as e:
        logger.error(f"❌ ERRO ao analisar WSDL: {str(e)}")
        return []

def analyze_wsdl_details():
    """Análise detalhada do WSDL"""
    wsdl_url = "https://elpusonlinelisboaqa.ipam.pt/WebSAPI/websapi.asmx?WSDL"
    
    try:
        logger.info("🔍 ANÁLISE DETALHADA DO WSDL")
        
        client = Client(wsdl_url)
        
        # Informações do serviço
        logger.info("📋 INFORMAÇÕES DO SERVIÇO:")
        logger.info(f"   🔹 Nome do serviço: {client.wsdl.services}")
        
        # Bindings disponíveis
        logger.info("📋 BINDINGS DISPONÍVEIS:")
        for binding_name, binding in client.wsdl.bindings.items():
            logger.info(f"   🔹 {binding_name}")
        
        # Tipos disponíveis
        logger.info("📋 TIPOS DE DADOS:")
        for type_name, type_obj in client.wsdl.types.items():
            logger.info(f"   🔹 {type_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ERRO na análise detalhada: {str(e)}")
        return False

def main():
    """Função principal"""
    
    logger.info("🎯 DESCOBERTA COMPLETA DE FUNÇÕES SOAP")
    logger.info("👤 Paulo - Professional Services")
    
    # Descobrir todas as operações
    all_operations = discover_all_soap_operations()
    
    if all_operations:
        logger.info(f"🎉 SUCESSO! Descobrimos {len(all_operations)} operações!")
        
        # Análise detalhada
        analyze_wsdl_details()
        
        # Comparação com nossas 10 funções selecionadas
        our_selected_functions = [
            'GetInst', 'GetAlunos', 'GetDocentes', 'GetCursos', 
            'GetAnosLect', 'GetPeriodos', 'GetTpCursos', 'ValidaLogin',
            'GetAluDadosPessoais', 'GetFunDadosPessoais'
        ]
        
        logger.info("📊 COMPARAÇÃO COM NOSSAS 10 FUNÇÕES SELECIONADAS:")
        
        found_our_functions = []
        for func in our_selected_functions:
            if func in all_operations:
                found_our_functions.append(func)
                logger.info(f"   ✅ {func} - ENCONTRADA")
            else:
                logger.info(f"   ❌ {func} - NÃO ENCONTRADA")
        
        logger.info(f"   📊 Das nossas 10 funções: {len(found_our_functions)} encontradas")
        
        # Funções adicionais que descobrimos
        additional_functions = [op for op in all_operations if op not in our_selected_functions]
        
        if additional_functions:
            logger.info(f"🔍 FUNÇÕES ADICIONAIS DESCOBERTAS ({len(additional_functions)}):")
            for func in additional_functions[:20]:  # Mostrar apenas as primeiras 20
                logger.info(f"   🔹 {func}")
            
            if len(additional_functions) > 20:
                logger.info(f"   ... e mais {len(additional_functions) - 20} funções")
        
    else:
        logger.warning("⚠️ Não foi possível descobrir as operações")
    
    # Write final summary
    with open(log_file_path, 'a', encoding='utf-8') as f:
        f.write(f"\n\n## 🎉 Resumo Final\n")
        f.write(f"- **Total de operações descobertas:** {len(all_operations)}\n")
        f.write(f"- **Status:** {'Sucesso' if all_operations else 'Falha'}\n")
        f.write(f"- **Endpoint funcional:** {'Sim' if all_operations else 'Não'}\n")
        f.write(f"\n---\n**Descoberta realizada em:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    logger.info(f"📄 Log completo salvo em: {log_file_path}")

if __name__ == "__main__":
    main() 