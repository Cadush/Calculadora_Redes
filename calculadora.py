# calculadora_redes.py

import ipaddress
from typing import Dict, List

class CalculadoraRedes:
    def calcular_subrede(self, rede: str) -> Dict:
        try:
            if '/' not in rede and ' ' in rede:
                ip, mascara = rede.split()
                rede = f"{ip}/{self.mascara_para_cidr(mascara)}"
            
            net = ipaddress.IPv4Network(rede, strict=False)
            
            hosts = list(net.hosts())
            return {
                "rede": str(net.network_address),
                "mascara": str(net.netmask),
                "cidr": net.prefixlen,
                "broadcast": str(net.broadcast_address),
                "primeiro_host": str(hosts[0]) if len(hosts) > 0 else None,
                "ultimo_host": str(hosts[-1]) if len(hosts) > 0 else None,
                "total_enderecos": net.num_addresses,
                "hosts_disponiveis": net.num_addresses - 2 if net.num_addresses > 2 else 0,
                "wildcard": str(net.hostmask),
                "classe": self.obter_classe(net.network_address),
                "privada": net.is_private,
                "valida": True
            }
        except Exception as e:
            return {"valida": False, "erro": str(e)}

    def subnetting(self, rede_base: str, hosts_por_rede: List[int]) -> List[Dict]:
        try:
            net = ipaddress.IPv4Network(rede_base, strict=False)
            subredes = []
            endereco_atual = net.network_address

            for hosts in hosts_por_rede:
                bits = 0
                while (2 ** bits) < (hosts + 2):
                    bits += 1
                prefixo = 32 - bits
                subrede = ipaddress.IPv4Network(f"{endereco_atual}/{prefixo}", strict=False)
                info = self.calcular_subrede(str(subrede))
                subredes.append(info)
                endereco_atual = subrede.broadcast_address + 1
                if endereco_atual > net.broadcast_address:
                    break
            return subredes
        except Exception as e:
            return [{"valida": False, "erro": str(e)}]

    def dividir_em_vlan_subredes(self, rede_base: str, num_vlans: int) -> List[Dict]:
        try:
            net = ipaddress.IPv4Network(rede_base, strict=False)
            if num_vlans <= 0 or num_vlans > 2**16:
                raise ValueError("Número de VLANs inválido.")

            # Calcula o prefixo necessário
            import math
            prefixo = net.prefixlen
            while (2 ** (32 - prefixo)) // (2 ** (32 - net.prefixlen)) < num_vlans:
                prefixo += 1
                if prefixo > 30:
                    raise ValueError("Não há espaço para tantas sub-redes.")

            subredes = list(net.subnets(new_prefix=prefixo))[:num_vlans]
            resultado = []
            for i, sub in enumerate(subredes):
                info = self.calcular_subrede(str(sub))
                info["vlan_id"] = i + 10  # VLANs começando em 10
                resultado.append(info)
            return resultado
        except Exception as e:
            return [{"valida": False, "erro": str(e)}]

    def mascara_para_cidr(self, mascara: str) -> int:
        return sum(bin(int(x)).count('1') for x in mascara.split('.'))

    def obter_classe(self, ip) -> str:
        first = int(str(ip).split('.')[0])
        if first <= 127: return 'A'
        elif first <= 191: return 'B'
        elif first <= 223: return 'C'
        elif first <= 239: return 'D'
        else: return 'E'


# ============ CLI AMIGÁVEL COM RICH (TERMINAL BONITO) ============
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.progress import track
import time

if __name__ == "__main__":
    console = Console()
    calc = CalculadoraRedes()

    console.print("\n" + "═" * 70, style="bold cyan")
    console.print("    NETWORK CALCULATOR PRO - TERMINAL EDITION".center(70), style="bold green")
    console.print("═" * 70 + "\n", style="bold cyan")

    while True:
        menu = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        menu.add_column("Opção", style="bold yellow")
        menu.add_column("Descrição", style="white")
        menu.add_row("1", "Subnetting por número de hosts + DNS")
        menu.add_row("2", "Dividir em VLANs iguais + DNS")
        menu.add_row("3", "Ambos (sem sobreposição)")
        menu.add_row("4", "Quantos IPs em um CIDR (ex: /20, /16)")
        menu.add_row("5", "Converter máscara → CIDR (ex: 10.0.0.0 255.255.255.248)")
        menu.add_row("6", "Identificar IP isolado (ex: 177.172.158.158)")
        menu.add_row("7", "Sair")
        console.print(menu)

        opcao = console.input("\n[bold yellow]➤ Escolha (1-7): [/]").strip()

        if opcao not in ["1", "2", "3", "4", "5", "6", "7"]:
            console.print("❌ Opção inválida!\n", style="bold red")
            continue
        if opcao == "7":
            console.print("\nSaindo... Até a próxima! 🚀\n", style="bold green")
            break

        # === Opção 4: Quantos IPs em um CIDR ===
        if opcao == "4":
            cidr_input = console.input("\n[bold cyan]Digite o CIDR[/] (ex: /20 ou 192.168.0.0/20): ").strip()
            try:
                if cidr_input.startswith("/"):
                    prefixo = int(cidr_input[1:])
                    total = 2 ** (32 - prefixo)
                    hosts = total - 2 if total > 2 else 0
                    mascara = str(ipaddress.IPv4Network(f"0.0.0.0/{prefixo}", strict=False).netmask)
                else:
                    net = ipaddress.IPv4Network(cidr_input, strict=False)
                    prefixo = net.prefixlen
                    total = net.num_addresses
                    hosts = total - 2 if total > 2 else 0
                    mascara = str(net.netmask)

                tabela = Table(title=f"CIDR /{prefixo}", box=box.ROUNDED)
                tabela.add_column("Campo", style="bold cyan")
                tabela.add_column("Valor", style="green")
                tabela.add_row("Prefixo", f"/{prefixo}")
                tabela.add_row("Máscara", mascara)
                tabela.add_row("Total de endereços", str(total))
                tabela.add_row("Hosts utilizáveis", str(hosts))
                console.print(Panel(tabela, style="bold green"))
            except Exception as e:
                console.print(f"❌ Erro: {e}\n", style="bold red")
            continue

        # === Opção 5: Converter máscara para CIDR ===
        if opcao == "5":
            entrada = console.input("\n[bold cyan]Digite IP + máscara[/] (ex: 10.0.0.0 255.255.255.248): ").strip()
            try:
                partes = entrada.split()
                if len(partes) != 2:
                    raise ValueError("Formato esperado: IP MÁSCARA (separados por espaço)")
                ip, mascara = partes
                cidr = calc.mascara_para_cidr(mascara)
                net = ipaddress.IPv4Network(f"{ip}/{cidr}", strict=False)
                total = net.num_addresses
                hosts = total - 2 if total > 2 else 0

                tabela = Table(title=f"Conversão: {mascara} → /{cidr}", box=box.ROUNDED)
                tabela.add_column("Campo", style="bold cyan")
                tabela.add_column("Valor", style="green")
                tabela.add_row("IP", ip)
                tabela.add_row("Máscara", mascara)
                tabela.add_row("CIDR", f"/{cidr}")
                tabela.add_row("Rede", str(net.network_address))
                tabela.add_row("Broadcast", str(net.broadcast_address))
                tabela.add_row("Total de endereços", str(total))
                tabela.add_row("Hosts utilizáveis", str(hosts))
                console.print(Panel(tabela, style="bold green"))
            except Exception as e:
                console.print(f"❌ Erro: {e}\n", style="bold red")
            continue

        # === Opção 6: Identificar IP isolado ===
        if opcao == "6":
            ip_input = console.input("\n[bold cyan]Digite o IP[/] (ex: 177.172.158.158): ").strip()
            try:
                ip_obj = ipaddress.IPv4Address(ip_input)
                tabela = Table(title=f"IP: {ip_input}", box=box.ROUNDED)
                tabela.add_column("Campo", style="bold cyan")
                tabela.add_column("Valor", style="green")
                tabela.add_row("Endereço", str(ip_obj))
                tabela.add_row("CIDR (host único)", "/32")
                tabela.add_row("Máscara", "255.255.255.255")
                tabela.add_row("Tipo", "Host isolado (sem sub-rede especificada)")
                tabela.add_row("Classe", calc.obter_classe(ip_obj))
                tabela.add_row("Privado", "Sim" if ipaddress.IPv4Address(ip_input).is_private else "Não")
                console.print(Panel(tabela, style="bold green"))
                console.print("[dim]💡 Sem máscara informada, um IP isolado é sempre /32 (1 host).[/]\n")
            except Exception as e:
                console.print(f"❌ Erro: {e}\n", style="bold red")
            continue

        # === Entrada de dados ===
        rede_base = console.input(f"\n[bold cyan]Rede base[/] (ex: 192.168.202.0/24): ").strip()
        dns = console.input(f"[bold cyan]DNS[/] (ex: 8.8.8.8): ").strip() or "8.8.8.8"

        try:
            base_net = ipaddress.IPv4Network(rede_base, strict=False)
        except:
            console.print("❌ Rede inválida!\n", style="bold red")
            continue

        resultados = []
        endereco_atual = base_net.network_address

        # === Subnetting ===
        if opcao in ["1", "3"]:
            hosts_input = console.input("[bold cyan]Hosts por sub-rede[/] (ex: 100,50,20): ").strip()
            try:
                hosts_list = [int(h.strip()) for h in hosts_input.split(",") if h.strip().isdigit()]
            except:
                console.print("❌ Hosts inválidos!\n", style="bold red")
                continue

            console.print("\nCalculando subnetting...", style="bold magenta")
            for i in track(range(len(hosts_list)), description="Subnetting..."):
                time.sleep(0.1)
                hosts = hosts_list[i]
                bits = 0
                while (2 ** bits) < (hosts + 2):
                    bits += 1
                prefixo = 32 - bits
                subrede = ipaddress.IPv4Network(f"{endereco_atual}/{prefixo}", strict=False)

                info = calc.calcular_subrede(str(subrede))
                info["tipo"] = "SUBNET"
                info["id"] = f"S{i+1:02d}"
                info["dns"] = dns
                resultados.append(info)

                endereco_atual = subrede.broadcast_address + 1
                if endereco_atual >= base_net.broadcast_address:
                    console.print("Aviso: Espaço esgotado!", style="yellow")
                    break

        # === VLANs ===
        if opcao in ["2", "3"]:
            if opcao == "2":
                endereco_atual = base_net.network_address
            try:
                num_vlans = int(console.input(f"\n[bold cyan]Quantas VLANs?[/] "))
            except:
                console.print("❌ Número inválido!\n", style="bold red")
                continue

            import math
            bits_emprestados = math.ceil(math.log2(num_vlans))
            prefixo = base_net.prefixlen + bits_emprestados
            if prefixo > 30:
                console.print(f"Erro: Máximo {2**(30 - base_net.prefixlen)} VLANs!", style="bold red")
                continue

            subredes = list(base_net.subnets(new_prefix=prefixo))[:num_vlans]
            console.print(f"Dividindo em {num_vlans} VLANs...", style="bold magenta")
            for i in track(range(len(subredes)), description="VLANs..."):
                time.sleep(0.05)
                sub = subredes[i]
                if sub.network_address < endereco_atual:
                    continue
                info = calc.calcular_subrede(str(sub))
                info["tipo"] = "VLAN"
                info["id"] = f"V{10+i:02d}"
                info["dns"] = dns
                info["vlan_id"] = 10 + i
                info["nome_vlan"] = f"VLAN {10+i}"
                resultados.append(info)

        # === Exibir tabela resumida ===
        if resultados:
            tabela_resumo = Table(title=f"Rede: {rede_base} | DNS: {dns}", box=box.ROUNDED, show_lines=True)
            tabela_resumo.add_column("ID", style="bold cyan", width=5)
            tabela_resumo.add_column("Tipo", style="bold yellow", width=8)
            tabela_resumo.add_column("Rede", style="green", width=16)
            tabela_resumo.add_column("CIDR", style="magenta", width=6)
            tabela_resumo.add_column("Hosts", style="white", width=6)
            tabela_resumo.add_column("DNS", style="blue", width=15)
            tabela_resumo.add_column("Broadcast", style="dim", width=16)

            for r in resultados:
                if r["valida"]:
                    tabela_resumo.add_row(
                        r['id'],
                        r['tipo'],
                        r['rede'],
                        f"/{r['cidr']}",
                        str(r['hosts_disponiveis']),
                        r['dns'],
                        r['broadcast']
                    )
                else:
                    tabela_resumo.add_row("ERRO", "", "", "", "", "", r.get('erro', ''), style="bold red")

            console.print(Panel(tabela_resumo, style="bold green"))

            # === MODO DETALHADO ===
            detalhe = console.input("\n[bold yellow]Ver detalhes completos? (s/N): [/]").strip().lower()
            if detalhe == "s":
                tabela_detalhe = Table(title="DETALHES COMPLETOS (como no JSON)", box=box.DOUBLE, show_lines=True)
                campos = ["id", "tipo", "rede", "cidr", "mascara", "broadcast", "primeiro_host", "ultimo_host",
                          "total_enderecos", "hosts_disponiveis", "wildcard", "classe", "privada", "dns"]
                for campo in campos:
                    estilo = "bold cyan" if campo in ["id", "tipo"] else "white"
                    tabela_detalhe.add_column(campo.replace("_", " ").title(), style=estilo)

                for r in resultados:
                    if r["valida"]:
                        linha = []
                        for campo in campos:
                            valor = r.get(campo, "")
                            if campo == "cidr":
                                valor = f"/{valor}"
                            elif campo == "privada":
                                valor = "Sim" if valor else "Não"
                            linha.append(str(valor))
                        tabela_detalhe.add_row(*linha)
                    else:
                        tabela_detalhe.add_row("ERRO", *["" for _ in campos[1:]], r.get('erro', ''), style="bold red")

                console.print(Panel(tabela_detalhe, style="bold magenta"))

            # === Salvar JSON ===
            salvar = console.input("\n[bold yellow]Salvar como JSON? (s/N): [/]").strip().lower()
            if salvar == "s":
                import json
                nome = f"calc_{rede_base.replace('/', '_').replace('.', '')}.json"
                with open(nome, "w") as f:
                    json.dump(resultados, f, indent=2, ensure_ascii=False)
                console.print(f"JSON salvo: [bold green]{nome}[/]\n")
        else:
            console.print("Nenhum resultado gerado.\n", style="bold red")
