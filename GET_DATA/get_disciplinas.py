import os
import lxml.etree as etree
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime

def get_disciplinas(client, logger, ano_lectivo: int, periodos: list[int], suffix: str):
    """
    Chama o método GetDisc para os períodos fornecidos, salva os XMLs e consolida os resultados em um único Excel.
    Recebe o cliente SOAP, um logger, o ano lectivo, uma lista de IDs de períodos e o sufixo para o nome do ficheiro.
    """
    all_disciplinas_data = []
    
    logger.info(f"Iniciando a extração de disciplinas para o Ano Lectivo: {ano_lectivo} e Períodos: {periodos}")

    try:
        # Mapeamento dos campos de saída (24 campos)
        psaida_fields = 'CdDisc;DgCadeira;AbrCadeira;CdCurso;DgCurso;CdPEstudo;DgPEstudo;CdDivisao;DgDivisao;CdPeriodo;DgPeriodo;Estado;TpDisc;CdGrupOpc;DgGrupOpc;NHorasTeo;NHorasPraticas;NHorasTeoPraticas;NHorasSemEstagio;NHorasPraticaLab;NHorasLaboratorio;NHorasTrabCampo;NHorasOrientTutorial;NHorasOutra'
        columns = psaida_fields.split(';')
        field_mapping = {f'c{i+1}': col for i, col in enumerate(columns)}

        for periodo in periodos:
            logger.info(f"Consultando disciplinas para o Ano Lectivo {ano_lectivo} e Período {periodo}")
            
            p_entrada = f'CdPeriodo={periodo}'

            params = {
                'Funcao': 'GetDisc',
                'NivelComp': 0,
                'Certificado': '',
                'FormatoOutput': 0,
                'PEntrada': p_entrada,
                'PSaida': psaida_fields,
                'Agrupar': '',
                'UseParser': ''
            }
            response = client.service.Execute(**params)

            # --- Verificação de resposta vazia ---
            if "Não foi encontrado nenhum registo" in response:
                logger.warning(f"A API retornou 'Não foi encontrado nenhum registo.' para o período {periodo}. Continuando para o próximo.")
                continue

            # Salvar a Resposta XML
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            xml_filename = f"get_disc_ano{ano_lectivo}_periodo_{periodo}_response_{timestamp}.xml"
            xml_dir = "XML_FILES"
            os.makedirs(xml_dir, exist_ok=True)
            xml_filepath = os.path.join(xml_dir, xml_filename)
            
            xml_formatted = etree.fromstring(response.encode('utf-8'))
            xml_pretty_str = etree.tostring(xml_formatted, pretty_print=True).decode('utf-8')

            with open(xml_filepath, 'w', encoding='utf-8') as f:
                f.write(xml_pretty_str)
            logger.info(f"Resposta XML salva em: {xml_filepath}")

            # Parse do XML
            root = ET.fromstring(xml_pretty_str)
            disciplinas_periodo_count = 0
            for resultado in root.findall('.//resultado'):
                # Pular registos que são na verdade mensagens de erro
                if len(resultado) == 1 and resultado.find('c1') is not None and "Não foi encontrado nenhum registo" in resultado.find('c1').text:
                    continue

                disciplina = {}
                for xml_field, df_field in field_mapping.items():
                    element = resultado.find(xml_field)
                    disciplina[df_field] = element.text.strip() if element is not None and element.text else ''
                all_disciplinas_data.append(disciplina)
                disciplinas_periodo_count += 1
            
            if disciplinas_periodo_count > 0:
                logger.info(f"{disciplinas_periodo_count} disciplinas processadas para o período {periodo}.")
            else:
                logger.info(f"Nenhuma disciplina válida encontrada para o período {periodo} após a filtragem.")

        if not all_disciplinas_data:
            logger.warning("Nenhuma disciplina foi encontrada em nenhum dos períodos consultados.")
            return None

        df = pd.DataFrame(all_disciplinas_data)
        logger.info(f"Total de {len(df)} disciplinas consolidadas de todos os períodos.")

        # Usar o caminho DATA_PROCESS/INSTITUTION/DATA_SOPHIA
        data_process_dir = "DATA_PROCESS"
        institution_dir = os.path.join(data_process_dir, suffix)  # Usa o sufixo da instituição (ex: EU para QA)
        data_sophia_dir = os.path.join(institution_dir, "DATA_SOPHIA")
        os.makedirs(data_sophia_dir, exist_ok=True)

        excel_filename = f"Disciplinas_{suffix}_Ano{ano_lectivo}.xlsx"
        excel_filepath = os.path.join(data_sophia_dir, excel_filename)

        df.to_excel(excel_filepath, index=False, sheet_name="Disciplinas", freeze_panes=(1,0))
        
        logger.info(f"Arquivo Excel consolidado gerado com sucesso em: {excel_filepath}")
        return df

    except Exception as e:
        logger.error(f"Ocorreu um erro em get_disciplinas: {e}", exc_info=True)
        return None
