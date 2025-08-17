import os
import lxml.etree as etree
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime

def get_ano_curr(client, logger, suffix):
    """
    Chama o método GetAnoCurr, salva o XML, converte para Excel e retorna o DataFrame.
    Recebe o cliente SOAP, um logger e um sufixo para o nome do arquivo.
    """
    try:
        # GetAnoCurr não precisa de parâmetros de entrada, todos são opcionais
        params = {
            'Funcao': 'GetAnoCurr',
            'NivelComp': 0,
            'FormatoOutput': 0,
            'PSaida': 'CdAnoCurr;AbrAnoCurr;DgAnoCurr',
            'Agrupar': '',
            'UseParser': ''
        }
        logger.info("Chamando o método 'Execute' para GetAnoCurr...")
        response = client.service.Execute(**params)

        if not response:
            logger.warning("A resposta do serviço para GetAnoCurr estava vazia.")
            return None

        # --- Salvar a Resposta XML ---
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        xml_filename = f"get_ano_curr_response_{timestamp}.xml"
        xml_filepath = os.path.join("XML_FILES", xml_filename)
        
        xml_formatted = etree.fromstring(response.encode('utf-8'))
        xml_pretty_str = etree.tostring(xml_formatted, pretty_print=True).decode('utf-8')

        with open(xml_filepath, 'w', encoding='utf-8') as f:
            f.write(xml_pretty_str)
        logger.info(f"Resposta XML salva em: {xml_filepath}")

        # --- Parse do XML e Conversão para DataFrame ---
        root = ET.fromstring(xml_pretty_str)
        data = []
        columns = ["CdAnoCurr", "AbrAnoCurr", "DgAnoCurr"]

        for resultado in root.findall('.//resultado'):
            cd_ano_curr_node = resultado.find('c1')
            abr_ano_curr_node = resultado.find('c2')
            dg_ano_curr_node = resultado.find('c3')
            if cd_ano_curr_node is not None and abr_ano_curr_node is not None and dg_ano_curr_node is not None:
                data.append([cd_ano_curr_node.text, abr_ano_curr_node.text, dg_ano_curr_node.text])

        df = pd.DataFrame(data, columns=columns)
        logger.info(f"{len(df)} anos curriculares processados.")

        # --- Salvar DataFrame em Excel ---
        excel_filename = f"AnoCurr_{suffix}.xlsx"
        excel_filepath = os.path.join("DATA_PROCESS", excel_filename)

        df.to_excel(excel_filepath, index=False, sheet_name="Anos_Curriculares")
        logger.info(f"Arquivo Excel gerado com sucesso em: {excel_filepath}")
        
        # Retorna o DataFrame para ser usado no script principal
        return df

    except Exception as e:
        logger.error(f"Ocorreu um erro em get_ano_curr: {e}", exc_info=True)
        return None
