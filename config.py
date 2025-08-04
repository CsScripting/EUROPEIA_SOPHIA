# Configuration settings

Europeia = "http://elpusonline.europeia.pt/websapi/websapi.asmx"
UE_IADE = "http://elpusonline.iade.pt/websapi/websapi.asmx"
IPAM_Porto = "http://elpusonlineporto.ipam.pt/websapi/websapi.asmx"
IPAM_Lisboa = "http://elpusonlinelisboa.ipam.pt/websapi/websapi.asmx"
QA = "https://elpusonlinelisboaqa.ipam.pt/WebSAPI/websapi.asmx"

# SOAP API Configuration
# WSDL_URL = Europeia + "?WSDL"

WSDL_URL = QA + "?WSDL"

# Determina o sufixo com base no WSDL_URL
if WSDL_URL == Europeia + "?WSDL":
    suffix = "E"
elif WSDL_URL == UE_IADE + "?WSDL":
    suffix = "I"
elif WSDL_URL == IPAM_Porto + "?WSDL":
    suffix = "P"
elif WSDL_URL == IPAM_Lisboa + "?WSDL":
    suffix = "L"
elif WSDL_URL == QA + "?WSDL":
    suffix = "QA"
else:
    # Caso nenhum dos URLs conhecidos seja usado, define um padrão e avisa.
    suffix = "Default"
    print(f"AVISO: O WSDL_URL '{WSDL_URL}' não é um dos URLs pré-configurados. Foi usado o sufixo padrão '{suffix}'.")

# Identity Server Configuration (Password Credentials Grant)
IDENTITY_SERVER_URL = "https://bullet-is-qa.europeia.pt/connect/token" 

CLIENT_ID = "Integration_2"
CLIENT_SECRET = "bulletOPT2006!"

USERNAME = "admin@bulletsolutions.com"
PASSWORD = "bulletOPT2006!"

# API Configuration
API_BASE_URL = "https://bullet-api-qa.europeia.pt/api"

# Source Endpoints / Templates
ACADEMIC_TERM_SEARCH_ENDPOINT = "/AcademicTerm/search" # Endpoint to search for AcademicTerm by name
ACADEMIC_YEAR_SEARCH_ENDPOINT = "/AcademicYear/search" # Endpoint to search for AcademicYear by name
MODULES_SEARCH_ENDPOINT = "/AcademicTermCurricularPlanModules/search" # Endpoint to search for modules by AcademicTerm ID
WLOADS_ENDPOINT_TEMPLATE = "/WLoads/by/{moduleIdentifier}/{academicTermIdentifier}" # Template for WLoads endpoint
TEACHER_GROUPS_ENDPOINT_TEMPLATE = "/WLoadTeacherGroups/all/by/{wLoadIdentifier}" # Template for Teacher Groups by WLoad ID

# Event Endpoints
EVENTS_SEARCH_ENDPOINT = "/Events/search" # Endpoint to search for existing Events

# Destination Endpoint
DESTINATION_ENDPOINT = "/Event" # Relative path for the destination endpoint (controller)

# Optional: Define scope if required by the Identity Server
SCOPE = "bestlegacy_api_scope"
