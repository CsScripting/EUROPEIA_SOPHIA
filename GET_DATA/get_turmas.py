import os
import lxml.etree as etree
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime

def get_turmas(client, logger, ano_lectivo: int, periodos: list[int], suffix: str):
    """
    Chama o método GetTurmas para um ano letivo e uma lista de períodos.
    Acumula os resultados, salva o XML e converte para um único ficheiro Excel.
    """
    logger.info(f"Iniciando a extração de turmas para o ano letivo: {ano_lectivo} e períodos: {periodos}")
    
    all_turmas_df = pd.DataFrame()
    xml_responses = []

    try:
        for periodo in periodos:
            logger.info(f"A obter turmas para o período: {periodo}")
            
            p_entrada = f"CdAnoLect={ano_lectivo};CdPeriodo={periodo}"

            params = {
                'Funcao': 'GetTurmas',
                'NivelComp': 0,
                'Certificado': '',
                'FormatoOutput': 0,
                'PEntrada': p_entrada,
                'PSaida': 'CdTurma;DgTurma;NumVagas',
                'Agrupar': '',
                'UseParser': ''
            }
            logger.debug(f"Chamando o método 'Execute' para GetTurmas com PEntrada: '{p_entrada}'")
            response = client.service.Execute(**params)
            
            # --- Verificação de resposta vazia ---
            if not response or "Não foi encontrado nenhum registo" in response:
                logger.warning(f"Nenhuma turma encontrada ou a API retornou 'Não foi encontrado nenhum registo.' para o período {periodo}. Continuando.")
                continue

            xml_responses.append(response)
            
            xml_formatted = etree.fromstring(response.encode('utf-8'))
            root = ET.fromstring(etree.tostring(xml_formatted))
            data = []
            columns = ["CdTurma", "DgTurma", "NumVagas"]

            for resultado in root.findall('.//resultado'):
                # Pular registos que são na verdade mensagens de erro
                if len(resultado) == 1 and resultado.find('c1') is not None and "Não foi encontrado nenhum registo" in resultado.find('c1').text:
                    continue
                
                cd_turma_node = resultado.find('c1')
                dg_turma_node = resultado.find('c2')
                num_vagas_node = resultado.find('c3')

                if cd_turma_node is not None:
                    data.append([
                        cd_turma_node.text,
                        dg_turma_node.text if dg_turma_node is not None else '',
                        num_vagas_node.text if num_vagas_node is not None else ''
                    ])

            if data:
                df_periodo = pd.DataFrame(data, columns=columns)
                logger.info(f"Encontradas {len(df_periodo)} turmas válidas para o período {periodo}.")
                all_turmas_df = pd.concat([all_turmas_df, df_periodo], ignore_index=True)
            else:
                logger.warning(f"Nenhuma turma válida encontrada para o período {periodo} após a filtragem.")

        if all_turmas_df.empty:
            logger.warning(f"Nenhuma turma encontrada para os critérios fornecidos em nenhum período.")
            return None
            
        logger.info(f"Total de turmas antes da remoção de duplicados: {len(all_turmas_df)}")
        all_turmas_df.drop_duplicates(inplace=True)
        logger.info(f"Total de turmas após remoção de duplicados: {len(all_turmas_df)}")

        all_turmas_df.sort_values(by=['DgTurma','CdTurma'], inplace=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        xml_dir = "XML_FILES"
        os.makedirs(xml_dir, exist_ok=True)
        xml_filename = f"get_turmas_ano{ano_lectivo}_p{'_'.join(map(str, periodos))}_response_{timestamp}.xml"
        xml_filepath = os.path.join(xml_dir, xml_filename)
        
        consolidated_root = etree.Element("resultados_consolidados")
        for res_text in xml_responses:
            try:
                # Apenas adiciona ao XML consolidado se não for uma mensagem de erro
                if "Não foi encontrado nenhum registo" not in res_text:
                    res_xml = etree.fromstring(res_text.encode('utf-8'))
                    consolidated_root.append(res_xml)
            except etree.XMLSyntaxError as e:
                logger.error(f"Erro ao fazer parse de uma resposta XML: {e}")

        xml_pretty_str = etree.tostring(consolidated_root, pretty_print=True).decode('utf-8')
        with open(xml_filepath, 'w', encoding='utf-8') as f:
            f.write(xml_pretty_str)
        logger.info(f"Respostas XML consolidadas salvas em: {xml_filepath}")

        output_dir = "DATA_PROCESS"
        os.makedirs(output_dir, exist_ok=True)
        excel_filename = f"Turmas_{suffix}_Ano{ano_lectivo}.xlsx"
        excel_filepath = os.path.join(output_dir, excel_filename)
        all_turmas_df.to_excel(excel_filepath, index=False, sheet_name="Turmas")
        
        logger.info(f"Arquivo Excel consolidado gerado com sucesso em: {excel_filepath}")
        return all_turmas_df

    except Exception as e:
        logger.error(f"Ocorreu um erro em get_turmas: {e}", exc_info=True)
        return None
