import os
import lxml.etree as etree
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime

def get_periodos(client, logger, suffix):
    """
    Chama o método GetPeriodos, salva o XML, converte para Excel e retorna o DataFrame.
    Recebe o cliente SOAP, um logger e um sufixo para o nome do arquivo.
    """
    try:
        params = {
            'Funcao': 'GetPeriodos',
            'NivelComp': 0,
            'Certificado': '',
            'FormatoOutput': 0,
            'PEntrada': '',
            'PSaida': 'CdPeriodo;DgPeriodo',
            'Agrupar': '',
            'UseParser': ''
        }
        logger.info("Chamando o método 'Execute' para GetPeriodos...")
        response = client.service.Execute(**params)

        if not response:
            logger.warning("A resposta do serviço para GetPeriodos estava vazia.")
            return None

        # --- Salvar a Resposta XML ---
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        xml_filename = f"get_periodos_response_{timestamp}.xml"
        xml_filepath = os.path.join("XML_FILES", xml_filename)
        
        xml_formatted = etree.fromstring(response.encode('utf-8'))
        xml_pretty_str = etree.tostring(xml_formatted, pretty_print=True).decode('utf-8')

        with open(xml_filepath, 'w', encoding='utf-8') as f:
            f.write(xml_pretty_str)
        logger.info(f"Resposta XML salva em: {xml_filepath}")

        # --- Parse do XML e Conversão para DataFrame ---
        root = ET.fromstring(xml_pretty_str)
        data = []
        columns = ["CdPeriodo", "DgPeriodo"]

        for resultado in root.findall('.//resultado'):
            cd_periodo_node = resultado.find('c1')
            dg_periodo_node = resultado.find('c2')
            if cd_periodo_node is not None and dg_periodo_node is not None:
                data.append([cd_periodo_node.text, dg_periodo_node.text])

        df = pd.DataFrame(data, columns=columns)
        logger.info(f"{len(df)} períodos processados.")

        # --- Salvar DataFrame em Excel ---
        # Usar o caminho DATA_PROCESS/INSTITUTION/DATA_SOPHIA
        data_process_dir = "DATA_PROCESS"
        institution_dir = os.path.join(data_process_dir, suffix)  # Usa o sufixo da instituição (ex: EU para QA)
        data_sophia_dir = os.path.join(institution_dir, "DATA_SOPHIA")
        os.makedirs(data_sophia_dir, exist_ok=True)

        excel_filename = f"Periodos_{suffix}.xlsx"
        excel_filepath = os.path.join(data_sophia_dir, excel_filename)

        df.to_excel(excel_filepath, index=False, sheet_name="Periodos", freeze_panes=(1,0))
        logger.info(f"Arquivo Excel gerado com sucesso em: {excel_filepath}")
        
        # Retorna o DataFrame para ser usado no script principal
        return df

    except Exception as e:
        logger.error(f"Ocorreu um erro em get_periodos: {e}", exc_info=True)
        return None
