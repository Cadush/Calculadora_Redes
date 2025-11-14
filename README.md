# Calculadora_Redes

![Badge em Desenvolvimento](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Rich](https://img.shields.io/badge/Interface-Rich%20Terminal-magenta)

> Uma **calculadora de sub-redes IPv4** com interface de terminal colorida e interativa, feita com `ipaddress` e `rich`.  
> Ideal para **técnicos de rede, CCNA, administradores e estudantes** que precisam de subnetting rápido e visual.

---

## Funcionalidades

| Recurso | Descrição |
|--------|-----------|
| **Cálculo de Sub-rede** | Rede, máscara, broadcast, hosts, wildcard, classe, privada |
| **Subnetting por Hosts** | Divide a rede em sub-redes com base no número de hosts desejado |
| **Divisão por VLANs** | Cria sub-redes iguais para N VLANs (com ID e nome) |
| **Modo Combinado** | Subnetting + VLANs sem sobreposição |
| **Interface Rica (Rich)** | Tabelas coloridas, progresso, painéis e entrada amigável |
| **Exportar JSON** | Salva todos os resultados em arquivo `.json` |
| **DNS Personalizado** | Adiciona DNS em cada sub-rede (ex: 8.8.8.8) |

---

## Instalação

### Requisitos
- Python 3.8+
- `pip`

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USUARIO/Calculadora_Redes.git
cd Calculadora_Redes

# 2. (Opcional) Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

### Uso
Execute o script diretamente:
python calculadora_redes.py


# 3. Instale a dependência
pip install rich
