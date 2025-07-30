# The Forge - Ambiente Virtual

## Configuração do Ambiente Virtual

Este projeto agora usa um ambiente virtual Python para garantir que todas as dependências estejam corretamente instaladas.

### Como Executar

#### Opção 1: Scripts Automáticos (Recomendado)

**Windows (CMD):**
```cmd
run_forge.bat
```

**Windows (PowerShell):**
```powershell
.\run_forge.ps1
```

#### Opção 2: Ativação Manual

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
python forge_qt_app.py
```

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
python forge_qt_app.py
```

### Dependências Instaladas

O ambiente virtual inclui:
- `openpyxl` - Para manipulação de arquivos Excel
- `jsonschema` - Para validação de JSON
- `pillow` - Para processamento de imagens
- `PySide6` - Para interface gráfica
- `pandas` - Para validação pós-processamento
- `lxml` - Para parsing XML

### Solução de Problemas

Se você encontrar o erro `No module named 'pandas'`:

1. Certifique-se de que o venv está ativado (deve aparecer `(venv)` no prompt)
2. Execute: `pip install -r requirements.txt`
3. Use os scripts automáticos para executar a aplicação

### Verificação

Para verificar se tudo está funcionando:
```bash
python -c "import pandas, openpyxl, PySide6; print('Todas as dependências estão instaladas!')"
``` 