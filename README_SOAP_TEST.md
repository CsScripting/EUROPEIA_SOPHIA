# Teste Serviço SOAP - GetFunctionDetail

Script simples para testar a operação `GetFunctionDetail` do serviço SOAP.

## Instalação

1. Instalar dependências:
```bash
pip install -r requirements.txt
```

## Uso

Executar o script:
```bash
python test_soap_function_details.py
```

## O que o script faz

1. **Testa operação Info** - Operação mais simples sem parâmetros para verificar conectividade
2. **Testa GetFunctionDetail** - Obtém detalhes de uma função específica

## Parâmetros GetFunctionDetail

- `NomeFunc`: Nome da função (ex: 'TEST')
- `FormatoInput`: Formato de entrada (ex: 'JSON', 'XML')  
- `FormatoOutput`: Formato de saída (ex: 'JSON', 'XML')

## Personalização

Edite os parâmetros na função `test_get_function_detail()` conforme suas necessidades:

```python
params = {
    'NomeFunc': 'SUA_FUNCAO',
    'FormatoInput': 'JSON',
    'FormatoOutput': 'JSON'
}
```

## Serviço

- URL: https://elpusonlinelisboaqa.ipam.pt/WebSAPI/
- WSDL: https://elpusonlinelisboaqa.ipam.pt/WebSAPI/websapi.asmx?WSDL 