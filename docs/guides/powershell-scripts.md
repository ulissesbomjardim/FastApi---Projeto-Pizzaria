# 🚀 Scripts de Automação - Hashtag Pizzaria

## Para Windows PowerShell

### setup.ps1 - Setup Completo
```powershell
# 🍕 Setup automático do projeto
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && chmod +x ./scripts/*.sh && ./scripts/setup.sh'
```

### start.ps1 - Iniciar Projeto  
```powershell
# 🚀 Iniciar todos os serviços
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && ./scripts/dev-commands.sh start'
```

### stop.ps1 - Parar Projeto
```powershell  
# 🛑 Parar todos os serviços
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && ./scripts/dev-commands.sh stop'
```

### status.ps1 - Ver Status
```powershell
# 📊 Status dos containers e conectividade
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && ./scripts/dev-commands.sh status'
```

### logs.ps1 - Ver Logs
```powershell
# 📋 Logs em tempo real
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && ./scripts/dev-commands.sh logs'
```

### clean.ps1 - Limpeza Completa
```powershell
# 🧹 Limpeza e rebuild completo
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && ./scripts/dev-commands.sh clean'
```

## Como Criar os Scripts

Execute estes comandos no PowerShell para criar os scripts:

```powershell
# Criar scripts directory
New-Item -ItemType Directory -Path "scripts\powershell" -Force

# Script de setup
@"
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && chmod +x ./scripts/*.sh && ./scripts/setup.sh'
"@ | Out-File -FilePath "scripts\powershell\setup.ps1" -Encoding utf8

# Script de start
@"
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && ./scripts/dev-commands.sh start'
"@ | Out-File -FilePath "scripts\powershell\start.ps1" -Encoding utf8

# Script de stop  
@"
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && ./scripts/dev-commands.sh stop'
"@ | Out-File -FilePath "scripts\powershell\stop.ps1" -Encoding utf8

# Script de status
@"
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && ./scripts/dev-commands.sh status'
"@ | Out-File -FilePath "scripts\powershell\status.ps1" -Encoding utf8

# Script de logs
@"
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && ./scripts/dev-commands.sh logs'
"@ | Out-File -FilePath "scripts\powershell\logs.ps1" -Encoding utf8

# Script de clean
@"
wsl -e bash -c 'cd "/mnt/g/dev/Hashtag/FastApi - Projeto Pizzaria" && ./scripts/dev-commands.sh clean'
"@ | Out-File -FilePath "scripts\powershell\clean.ps1" -Encoding utf8
```

## Uso dos Scripts

```powershell
# Setup inicial (primeira vez)
.\scripts\powershell\setup.ps1

# Uso diário
.\scripts\powershell\start.ps1     # Iniciar
.\scripts\powershell\status.ps1    # Ver status  
.\scripts\powershell\logs.ps1      # Ver logs
.\scripts\powershell\stop.ps1      # Parar
.\scripts\powershell\clean.ps1     # Limpeza completa
```