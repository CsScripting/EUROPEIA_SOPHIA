#!/usr/bin/env python3
"""
Análise Detalhada dos 8 Endpoints SOAP Selecionados
Autor: Paulo - Professional Services
Objetivo: Analisar parâmetros de entrada, saída e detalhes técnicos dos endpoints selecionados
"""

from zeep import Client
import xml.etree.ElementTree as ET
from datetime import datetime
import logging
import os
import sys

# Adiciona o diretório raiz do projeto ao sys.path para que o 'config' seja encontrado
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from config import WSDL_URL

# --- Setup Logging ---
log_dir = "LOGS"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file_name = f"endpoint_analysis_8_selected_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"
log_file_path = os.path.join(log_dir, log_file_name)

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(message)s'))

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Lista dos 8 endpoints selecionados a analisar
ENDPOINTS_TO_ANALYZE = [
    'GetDocentes', 
    'GetCursos',
    'GetAnosLect',
    'GetAnoCurr',
    'GetPeriodos',
    'GetCursos',
    'GetPEstudos',
    'GetTurmas',
    'GetDisc',
    'GetDiscHorario',
    'EditLinhaHorario',
    'PutHorario'
]

def parse_function_detail_response(xml_string, function_name):
    """Parse corrigido da resposta do GetFunctionDetail"""
    try:
        result = {
            'function_name': function_name,
            'found': False,
            'description': '',
            'input_params': [],
            'output_params': [],
            'creation_date': '',
            'modification_date': '',
            'flag': '',
            'execution_mode': '',
            'code': '',
            'returns_bytes': '',
            'error_details': ''
        }
        
        # Verificar se é resposta de erro (função não encontrada)
        if '<EstRes>1</EstRes>' in xml_string and 'Não foi encontrado nenhum registo' in xml_string:
            result['error_details'] = 'Função não encontrada'
            return result
        
        # Parse do XML usando regex para ser mais robusto
        import re
        
        # Verificar se encontrou a função
        if '<FunctionDetail>' in xml_string:
            result['found'] = True
            
            # Extrair código do procedimento
            code_match = re.search(r'<CdProc>([^<]*)</CdProc>', xml_string)
            if code_match:
                result['code'] = code_match.group(1)
            
            # Extrair descrição
            desc_match = re.search(r'<Descricao><!\[CDATA\[([^\]]*)\]\]></Descricao>', xml_string)
            if desc_match:
                result['description'] = desc_match.group(1)
            
            # Extrair datas
            dt_criacao_match = re.search(r'<DtCriacao[^>]*>([^<]*)</DtCriacao>', xml_string)
            if dt_criacao_match and dt_criacao_match.group(1).strip():
                result['creation_date'] = dt_criacao_match.group(1)
            
            dt_alteracao_match = re.search(r'<DtAlteracao[^>]*>([^<]*)</DtAlteracao>', xml_string)
            if dt_alteracao_match and dt_alteracao_match.group(1).strip():
                result['modification_date'] = dt_alteracao_match.group(1)
            
            # Extrair flag e modo de execução
            flag_match = re.search(r'<Flag>([^<]*)</Flag>', xml_string)
            if flag_match:
                result['flag'] = flag_match.group(1)
            
            modo_match = re.search(r'<ModoExec>([^<]*)</ModoExec>', xml_string)
            if modo_match:
                result['execution_mode'] = modo_match.group(1)
            
            bytes_match = re.search(r'<DevolveBytes>([^<]*)</DevolveBytes>', xml_string)
            if bytes_match:
                result['returns_bytes'] = bytes_match.group(1)
            
            # Extrair parâmetros de entrada (note o erro de digitação no sistema)
            entrada_match = re.search(r'<ParamentrosEntrada>([^<]*)</ParamentrosEntrada>', xml_string)
            if entrada_match:
                entrada_text = entrada_match.group(1)
                if entrada_text and entrada_text.lower() != 'nenhum':
                    result['input_params'] = parse_parameters(entrada_text)
            
            # Extrair parâmetros de saída
            saida_match = re.search(r'<ParametrosSaida>([^<]*)</ParametrosSaida>', xml_string)
            if saida_match:
                saida_text = saida_match.group(1)
                if saida_text and saida_text.lower() not in ['nenhum', '']:
                    result['output_params'] = parse_parameters(saida_text)
        
        return result
        
    except Exception as e:
        logger.error(f'Parse error para {function_name}: {e}')
        return {
            'function_name': function_name,
            'found': False,
            'error_details': f'Parse error: {e}',
            'description': '',
            'input_params': [],
            'output_params': []
        }

def parse_parameters(param_string):
    """Parse de string de parâmetros em lista estruturada"""
    if not param_string or param_string.strip() == '' or param_string.lower() == 'nenhum':
        return []
    
    # Separar por ; principalmente
    params = []
    if ';' in param_string:
        parts = [p.strip() for p in param_string.split(';') if p.strip()]
        params = [{'name': p, 'type': 'string', 'description': ''} for p in parts]
    elif ',' in param_string:
        parts = [p.strip() for p in param_string.split(',') if p.strip()]
        params = [{'name': p, 'type': 'string', 'description': ''} for p in parts]
    else:
        # Único parâmetro
        params = [{'name': param_string.strip(), 'type': 'string', 'description': ''}]
    
    return params

def analyze_endpoint(function_name):
    """Analisa um endpoint específico usando GetFunctionDetail"""
    wsdl_url_to_use = WSDL_URL
    
    try:
        client = Client(wsdl_url_to_use)
        
        logger.info(f"🔍 Analisando: {function_name}")
        
        # Chamar GetFunctionDetail
        response = client.service.GetFunctionDetail(function_name)
        
        # Parse da resposta
        result = parse_function_detail_response(response, function_name)
        
        if result['found']:
            logger.info(f"   ✅ Função encontrada! (Código: {result['code']})")
            logger.info(f"   📝 Descrição: {result['description'][:80]}...")
            logger.info(f"   📥 Parâmetros entrada: {len(result['input_params'])}")
            logger.info(f"   📤 Parâmetros saída: {len(result['output_params'])}")
            if result['output_params']:
                logger.info(f"   📋 Campos saída: {[p['name'] for p in result['output_params'][:3]]}...")
        else:
            logger.warning(f"   ❌ Erro: {result['error_details']}")
        
        return result
        
    except Exception as e:
        logger.error(f"   ❌ Erro técnico: {str(e)}")
        return {
            'function_name': function_name,
            'found': False,
            'error_details': f'Erro técnico: {str(e)}',
            'description': '',
            'input_params': [],
            'output_params': []
        }

def generate_markdown_report(analysis_results):
    """Gera relatório detalhado em Markdown"""
    
    # Cabeçalho do relatório
    with open(log_file_path, 'w', encoding='utf-8') as f:
        f.write(f"# 📊 Análise Detalhada dos 8 Endpoints SOAP Selecionados\n")
        f.write(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"**Autor:** Paulo - Professional Services  \n")
        f.write(f"**Objetivo:** Análise técnica completa dos endpoints selecionados\n\n")
        
        # Lista dos 8 endpoints a analisar
        f.write(f"## 🎯 Endpoints Selecionados para Análise\n\n")
        for i, endpoint in enumerate(ENDPOINTS_TO_ANALYZE, 1):
            f.write(f"{i}. **`{endpoint}`**\n")
        f.write(f"\n---\n\n")
        
        # Resumo executivo
        found_count = sum(1 for r in analysis_results if r['found'])
        f.write(f"## 📋 Resumo Executivo\n")
        f.write(f"- **Total de endpoints analisados:** {len(analysis_results)}\n")
        f.write(f"- **Endpoints encontrados:** {found_count}/{len(analysis_results)} ({found_count/len(analysis_results)*100:.1f}%)\n")
        f.write(f"- **Endpoints com erro:** {len(analysis_results)-found_count}\n\n")
        

        
        # Análise detalhada por endpoint
        f.write(f"## 🔍 Análise Detalhada por Endpoint\n\n")
        
        for result in analysis_results:
            f.write(f"### {result['function_name']}\n")
            
            if result['found']:
                f.write(f"**Status:** ✅ Disponível  \n")
                f.write(f"**Código:** {result.get('code', 'N/A')}  \n")
                f.write(f"**Descrição:** {result['description']}  \n")
                
                if result['creation_date']:
                    f.write(f"**Criado em:** {result['creation_date']}  \n")
                if result['modification_date']:
                    f.write(f"**Modificado em:** {result['modification_date']}  \n")
                if result['flag']:
                    flag_desc = "Função de consulta" if result['flag'] == '0' else "Função de alteração"
                    f.write(f"**Flag:** {result['flag']} ({flag_desc})  \n")
                if result['execution_mode']:
                    f.write(f"**Modo de execução:** {result['execution_mode']}  \n")
                if result['returns_bytes']:
                    bytes_desc = "Sim" if result['returns_bytes'] == 'S' else "Não"
                    f.write(f"**Retorna bytes:** {bytes_desc}  \n")
                
                # Parâmetros de entrada
                f.write(f"\n#### 📥 Parâmetros de Entrada\n")
                if result['input_params']:
                    for param in result['input_params']:
                        f.write(f"- `{param['name']}`\n")
                else:
                    f.write(f"*Nenhum parâmetro de entrada obrigatório*\n")
                
                # Parâmetros de saída
                f.write(f"\n#### 📤 Parâmetros de Saída\n")
                if result['output_params']:
                    for param in result['output_params']:
                        f.write(f"- `{param['name']}`\n")
                else:
                    f.write(f"*Parâmetros de saída não especificados*\n")
                
                # Exemplo de chamada (comentado)
                # f.write(f"\n#### 🔧 Exemplo de Chamada Execute\n")
                # f.write(f"```python\n")
                # f.write(f"params = {{\n")
                # f.write(f"    'Funcao': '{result['function_name']}',\n")
                # f.write(f"    'NivelComp': 0,\n")
                # f.write(f"    'Certificado': '',\n")
                # f.write(f"    'FormatoOutput': 0,\n")
                # f.write(f"    'PEntrada': '',  # Ajustar se necessário\n")
                # if result['output_params']:
                #     output_fields = ';'.join([p['name'] for p in result['output_params']])
                #     f.write(f"    'PSaida': '{output_fields}',\n")
                # else:
                #     f.write(f"    'PSaida': '',\n")
                # f.write(f"    'Agrupar': '',\n")
                # f.write(f"    'UseParser': ''\n")
                # f.write(f"}}\n")
                # f.write(f"response = client.service.Execute(**params)\n")
                # f.write(f"```\n")
                
            else:
                f.write(f"**Status:** ❌ Erro  \n")
                f.write(f"**Detalhes:** {result['error_details']}  \n")
            
            f.write(f"\n---\n\n")
        
        # Recomendações
        f.write(f"## 💡 Recomendações de Implementação\n\n")
        
        working_endpoints = [r for r in analysis_results if r['found']]
        error_endpoints = [r for r in analysis_results if not r['found']]
        
        if working_endpoints:
            f.write(f"### ✅ Endpoints Prontos para Implementação\n")
            for result in working_endpoints:
                complexity = "Simples" if not result['input_params'] else "Requer parâmetros"
                f.write(f"- **`{result['function_name']}`** ({complexity}): {result['description']}\n")
            f.write(f"\n")
        
        if error_endpoints:
            f.write(f"### ⚠️ Endpoints que Requerem Investigação\n")
            for result in error_endpoints:
                f.write(f"- **`{result['function_name']}`**: {result['error_details']}\n")
            f.write(f"\n")
        
        f.write(f"### 🔧 Próximos Passos\n")
        f.write(f"1. **Implementar endpoints simples** (sem parâmetros de entrada)\n")
        f.write(f"2. **Testar chamadas Execute** com parâmetros de saída descobertos\n")
        f.write(f"3. **Investigar parâmetros de entrada** para funções mais complexas\n")
        f.write(f"4. **Configurar autenticação** se necessário para funções de edição\n\n")
        
        f.write(f"---\n**Relatório gerado em:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Função principal"""
    logger.info("📊 ANÁLISE DETALHADA DOS 8 ENDPOINTS SOAP SELECIONADOS")
    logger.info("👤 Paulo - Professional Services")
    logger.info(f"🎯 Analisando {len(ENDPOINTS_TO_ANALYZE)} endpoints selecionados")
    
    analysis_results = []
    
    for function_name in ENDPOINTS_TO_ANALYZE:
        result = analyze_endpoint(function_name)
        analysis_results.append(result)
    
    # Gerar relatório
    logger.info("📝 Gerando relatório detalhado...")
    generate_markdown_report(analysis_results)
    
    # Resumo final
    found_count = sum(1 for r in analysis_results if r['found'])
    logger.info(f"📊 RESUMO FINAL:")
    logger.info(f"   ✅ Endpoints encontrados: {found_count}/{len(analysis_results)}")
    logger.info(f"   ❌ Endpoints com erro: {len(analysis_results)-found_count}")
    logger.info(f"📄 Relatório salvo em: {log_file_path}")

if __name__ == "__main__":
    main() 