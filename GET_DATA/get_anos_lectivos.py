import os
import lxml.etree as etree
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime

def get_anos_lectivos(client, logger):
    """
    Chama o método GetAnosLect, salva o XML e converte para Excel.
    Recebe o cliente SOAP já inicializado e um logger.
    """
    try:
        # --- 1. Chamada da Função GetAnosLect ---
        params = {
            'Funcao': 'GetAnosLect',
            'NivelComp': 0,
            'Certificado': '',
            'FormatoOutput': 0,
            'PEntrada': '',
            'PSaida': 'CdAnoLect;AnoLect',
            'Agrupar': '',
            'UseParser': ''
        }
        logger.info("Chamando o método 'Execute' para GetAnosLect...")
        response = client.service.Execute(**params)
        
        # --- 2. Salvar a Resposta XML ---
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        xml_filename = f"get_anos_lectivos_response_{timestamp}.xml"
        xml_filepath = os.path.join("XML_FILES", xml_filename)

        xml_formatted = etree.fromstring(response.encode('utf-8'))
        xml_pretty_str = etree.tostring(xml_formatted, pretty_print=True).decode('utf-8')

        with open(xml_filepath, 'w', encoding='utf-8') as f:
            f.write(xml_pretty_str)
        logger.info(f"Resposta XML salva em: {xml_filepath}")

        # --- 3. Parse do XML e Conversão para DataFrame ---
        root = ET.fromstring(xml_pretty_str)
        
        data = []
        columns = ["CdAnoLect", "AnoLect"]

        for resultado in root.findall('resultado'):
            cd_ano_lect_node = resultado.find('c1')
            ano_lect_node = resultado.find('c2')

            if cd_ano_lect_node is not None and ano_lect_node is not None:
                cd_ano_lect = cd_ano_lect_node.text
                ano_lect = ano_lect_node.text
                data.append([cd_ano_lect, ano_lect])

        df = pd.DataFrame(data, columns=columns)
        logger.info(f"{len(df)} anos letivos processados.")

        # --- 4. Salvar DataFrame em Excel ---
        excel_filename = f"AnosLectivos_Sophia.xlsx"
        excel_filepath = os.path.join("XLSX_FILES", excel_filename)

        df.to_excel(excel_filepath, index=False, sheet_name="Anos_Lectivos")
        
        logger.info(f"Arquivo Excel gerado com sucesso em: {excel_filepath}")
        return True

    except Exception as e:
        logger.error(f"Ocorreu um erro em get_anos_lectivos: {e}")
        return False 