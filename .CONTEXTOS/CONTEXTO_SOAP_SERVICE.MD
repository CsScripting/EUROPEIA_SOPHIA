Sou o Paulo de Professional Services de Empresa de Software.

Tenho um Serviço de Integração para efetuar.
Antes de começar integrações queria testar as chamadas a serviço SOAP.

Gostaria de começar a testar as chamadas a este serviço com PYTHON.
O serviço de testes esta neste link:

 https://elpusonlinelisboaqa.ipam.pt/WebSAPI/

 A descrição de Serviço está no ficheiro websapi.xml que se encontra no caminho:

 .CONTEXTOS\websapi.xml



*	GET_EVENTS_BEST_PROD: 
o	fetch_events: todos os eventos relativos a Tipo de Evento: Aulas, Periodo Academico: 2025/2026 - 1º Semestre
Tem também os diferentes ficheiros filtrados por Instituição.

*	Ficheiros de Validação(REsultado de Module 3.validate_map_data):

o	Valid_data_BEST_X_2025_PRIMER: 
 

Binómio/dimensões SOPHIA, existentes em BEST e SOPHIA que irão permitir mapeamento de Dados;

o	Invalid_data_BEST_X_2025_PRIMER:

                             
Binómio/dimensões SOPHIA existentes em BEST, e sem correspondência em SOPHIA para uma das entidades associadas, que não irão permitir mapeamento de Dados;


o	INVALID_data_NHORARIOS_X_2025_PRIMER:

Linhas de Horarios em SOPHIA associadas a professores que não estão presentes em BEST, muitas vezes por não existir NContabilistico em SOPHIA para mapear para BEST.

o	VALID_data_NHORARIOS_X_2025_PRIMER:
Horarios SOPHIA com entidades mapeadas para Update …

* Ficheiros de validação (REsultado de Module 4.extract_schedules_update_2): 

o	BEST_MAP_NHORARIOS_X_2025_PRIMER

Relação de Dimensões SOPHIA existentes em BEST.
Indica se o que existe em BEST tem ou não Horário em SOPHIA…


o	NHORARIOS_FINAL_MAPPING_X_2025_PRIMER

 
Regras de Update associadas a Horarios de SOPHIA:

Três casos em particular:

	DSD BEST = N_LINHA_HORARIO

Apenas atualizar professores de acordo com BEST

	DSD BEST > N_LINHA_HORARIO

EX: Dois Professores em BEST, uma linha Horário. Atualizar linha horário se necessário, e fazer PUT_HORARIO com novo Professor(AINDA NÂO IMPLEMENTADO). 


	DSD BEST < N_LINHA_HORARIO

EX: Um Professores em BEST, Duas linha Horário. Atualizar um linha se necessário, outras linhas horário sem Professores.
Exceção: se DSD BEST = 0 não alterar linhas de Horarios de SOPHIA


o	UPDATED_NHORARIOS_FINAL_X_2025_PRIMER
Ficheiro com resultado de Updates.
