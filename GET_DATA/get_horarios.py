import os
import lxml.etree as etree
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime

def get_horarios(client, logger, ano_lectivo: int, periodos: list[int], suffix: str):
    """
    Chama o método GetDiscHorario para um ano letivo e uma lista de períodos.
    Acumula os resultados e salva num único ficheiro Excel.
    """
    logger.info(f"Iniciando a extração de horários para o Ano Letivo: {ano_lectivo} e Períodos: {periodos}")
    
    all_horarios_df = pd.DataFrame()
    xml_responses = []
    
    psaida_fields = 'CdTurma;DgTurma;DiaSemana;HoraIni;MinutoIni;HoraFim;MinutoFim;CdRegime;DgRegime;NmDocente;Sala;CdDocente;CdDis;NmDis;CdSala;CdPEstudo;AbrDis;CdCampus;CdEdificio;CdPiso;CdAulaFrequencia;DtProxima;CorHorarioWin32;IconRegime'
    columns = psaida_fields.split(';')
    field_mapping = {f'c{i+1}': col for i, col in enumerate(columns)}

    try:
        for periodo in periodos:
            logger.info(f"A obter horários para o período: {periodo}")
            
            params = {
                'Funcao': 'GetDiscHorario',
                'NivelComp': 0,
                'Certificado': '',
                'FormatoOutput': 0,
                'PEntrada': f'AnoLectivo={ano_lectivo};CdPeriodo={periodo}',
                'PSaida': psaida_fields,
                'Agrupar': '',
                'UseParser': ''
            }
            logger.debug(f"Chamando o método 'Execute' para GetDiscHorario com PEntrada: '{params['PEntrada']}'")
            response = client.service.Execute(**params)

            # --- Verificação de resposta vazia ---
            if not response or "Não foi encontrado nenhum registo" in response:
                logger.warning(f"Nenhum horário encontrado ou a API retornou 'Não foi encontrado nenhum registo.' para o período {periodo}. Continuando.")
                continue

            xml_responses.append(response)

            xml_formatted = etree.fromstring(response.encode('utf-8'))
            root = ET.fromstring(etree.tostring(xml_formatted))
            data = []

            for resultado in root.findall('.//resultado'):
                # Pular registos que são na verdade mensagens de erro
                if len(resultado) == 1 and resultado.find('c1') is not None and "Não foi encontrado nenhum registo" in resultado.find('c1').text:
                    continue
                horario = {df_field: resultado.find(xml_field).text.strip() if resultado.find(xml_field) is not None and resultado.find(xml_field).text else '' for xml_field, df_field in field_mapping.items()}
                data.append(horario)
            
            if data:
                df_periodo = pd.DataFrame(data)
                logger.info(f"Encontrados {len(df_periodo)} registos de horário válidos para o período {periodo}.")
                all_horarios_df = pd.concat([all_horarios_df, df_periodo], ignore_index=True)
            else:
                logger.warning(f"Nenhum horário válido encontrado para o período {periodo} após a filtragem.")

        if all_horarios_df.empty:
            logger.warning("Nenhum horário foi encontrado para os critérios fornecidos em nenhum período.")
            return None
        
        logger.info(f"Total de registos de horário antes da remoção de duplicados: {len(all_horarios_df)}")
        all_horarios_df.drop_duplicates(inplace=True)
        logger.info(f"Total de registos de horário após remoção de duplicados: {len(all_horarios_df)}")

        all_horarios_df.sort_values(by=['DgTurma','CdTurma'], inplace=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        xml_dir = "XML_FILES"
        os.makedirs(xml_dir, exist_ok=True)
        xml_filename = f"get_horarios_ano{ano_lectivo}_p{'_'.join(map(str, periodos))}_response_{timestamp}.xml"
        xml_filepath = os.path.join(xml_dir, xml_filename)
        
        consolidated_root = etree.Element("resultados_consolidados")
        for res_text in xml_responses:
            if "Não foi encontrado nenhum registo" not in res_text:
                try:
                    res_xml = etree.fromstring(res_text.encode('utf-8'))
                    consolidated_root.append(res_xml)
                except etree.XMLSyntaxError as e:
                    logger.error(f"Erro ao fazer parse de uma resposta XML para horários: {e}")

        xml_pretty_str = etree.tostring(consolidated_root, pretty_print=True).decode('utf-8')
        with open(xml_filepath, 'w', encoding='utf-8') as f:
            f.write(xml_pretty_str)
        logger.info(f"Respostas XML de horários consolidadas salvas em: {xml_filepath}")

        output_dir = "DATA_PROCESS"
        os.makedirs(output_dir, exist_ok=True)
        excel_filename = f"Horarios_{suffix}_Ano{ano_lectivo}.xlsx"
        excel_filepath = os.path.join(output_dir, excel_filename)
        all_horarios_df.to_excel(excel_filepath, index=False, sheet_name="Horarios")
        
        logger.info(f"Arquivo Excel de horários consolidado gerado com sucesso em: {excel_filepath}")
        return all_horarios_df

    except Exception as e:
        logger.error(f"Ocorreu um erro em get_horarios: {e}", exc_info=True)
        return None
