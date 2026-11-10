# Tarefa 1 a partir do rascunho de Henrique (texto_tarefa1.md), revisado.
# Executado dentro de build.py (usa d, para, bul, tbl, pend, Cm, Pt, WD_ALIGN_PARAGRAPH).
import re

SRC = '../Henrique_Tarefa1_handoff/texto_tarefa1.md'
PR = '../Henrique_Tarefa1_handoff/prints/'
md = open(SRC, encoding='utf-8').read()

# --- revisões de conteúdo ---
md = md.split('## 1. Verificação', 1)[1]
md = '## 1. Verificação' + md
md = md.split('## 9. Evidências')[0]

md = md.replace(
    "- Security Group g3-sc-wazuh: a porta 443 deixou de estar aberta para qualquer origem e foi restringida a um endereço /32 (print 17).",
    "- Security Group g3-sc-wazuh: a porta 443 deixou de estar aberta para qualquer origem e foi restringida a endereços /32 de integrantes (print 17 mostra a primeira restrição). Em 06/11/2026 a regra tinha entradas /32 individuais, identificadas na descrição de cada uma.")
md = md.replace(
    "- Limitação: hoje apenas um endereço IP tem acesso à porta 443. Os endereços dos demais integrantes ainda precisam ser incluídos. Não foi comprovado, por teste a partir de outro endereço, que o acesso é bloqueado; o resultado do Security Group foi conferido na configuração e o acesso foi validado a partir do endereço liberado.",
    "- Validação do bloqueio: em 06/11/2026, a partir de um endereço ainda não incluído na regra, https://zabbix.maisplace.net.br e https://monitoramento.maisplace.net.br não responderam (tempo esgotado). Depois da inclusão desse endereço /32, as duas interfaces responderam (200 e 302). Isso comprova que o controle está no Security Group, e não apenas no login.")
md = md.replace(
    "Recomenda-se aumentar a instância (por exemplo, t3.large, com 8 GiB) antes da integração, ou ao menos acompanhar o uso de memória e swap durante os testes.",
    "Recomenda-se aumentar a instância (por exemplo, t3.large, com 8 GiB) antes da integração, ou ao menos acompanhar o uso de memória e swap durante os testes. Na conferência de 06/11/2026 (14:16 UTC), já com db-01 e jump-01 no Zabbix, a instância tinha 942 MB disponíveis e 996 MB de swap em uso, e o Wazuh registrou um alerta de falta de memória (regra 5108) nela às 04:33 (horário local) do mesmo dia (seção 4.3).")
md = md.replace(
    "Nesta instalação o agent2 monitora o próprio servidor.",
    "Nesta instalação o agent2 monitora o próprio servidor, e foi instalado também no banco (db-01) e no jump server (jump-01) na Tarefa 2.")
for chk in ['restringida a endereços /32 de integrantes','Validação do bloqueio','942 MB disponíveis','instalado também no banco']:
    assert chk in md, chk

# print NN -> Figura 1.NN
def fig_ref(m):
    txt = m.group(0)
    nums = re.findall(r'\d+', txt)
    if len(nums) == 1:
        return 'Figura 1.%d' % int(nums[0])
    if ' a ' in txt:
        return 'Figuras 1.%d a 1.%d' % (int(nums[0]), int(nums[-1]))
    return 'Figuras ' + ' e '.join('1.%d' % int(n) for n in nums)
md = re.sub(r'prints? \d+( (a|e) \d+)?', fig_ref, md)


def runs_md(p, text):
    for i, part in enumerate(re.split(r'\*\*', text)):
        r = p.add_run(part)
        r.bold = (i % 2 == 1)


lines = md.split('\n')
i = 0
while i < len(lines):
    ln = lines[i].rstrip()
    if not ln:
        i += 1
        continue
    if ln.startswith('### '):
        d.add_heading(ln[4:].replace('Questão', 'Questão'), 3)
    elif ln.startswith('## '):
        d.add_heading(re.sub(r'^(\d+)\. ', lambda m: '1.' + m.group(1) + ' ', ln[3:]), 2)
    elif ln.startswith('|'):
        rows = []
        while i < len(lines) and lines[i].startswith('|'):
            cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
            if not all(set(c) <= set('-: ') for c in cells):
                rows.append(cells)
            i += 1
        tbl(rows)
        continue
    elif ln.startswith('- '):
        p = d.add_paragraph(style='List Bullet')
        runs_md(p, ln[2:])
    elif re.match(r'^\d+\. ', ln):
        p = d.add_paragraph(style='List Number')
        runs_md(p, re.sub(r'^\d+\. ', '', ln))
    else:
        p = d.add_paragraph()
        runs_md(p, ln)
    i += 1

d.add_heading('Evidências da Tarefa 1', 2)
CAPS = [
    ('01_ambiente_ec2_instancia.png', 'Instância g3-wazuh-server (t3.medium, 2 vCPU, 4 GiB) no console da AWS.'),
    ('02_antes_recursos_cpu_ram_disco.png', 'Antes da instalação (29/10/2026, 15:48 UTC): CPU, memória (1120 MB disponíveis, sem swap) e disco (17%).'),
    ('03_antes_servicos_portas_versoes_agentes.png', 'Antes da instalação: serviços e portas do Wazuh (443 do dashboard), versões e agentes ativos.'),
    ('04_swap_2gb_persistente.png', 'Swap de 2 GB persistente e swappiness 10 (29/10/2026, 16:13 UTC).'),
    ('05_versoes_instaladas.png', 'Versões instaladas: Zabbix 7.0.32, MySQL 8.4.11, nginx 1.28.3, PHP 8.5.4 e Wazuh 4.9.2.'),
    ('06_conflito_443_wazuh_e_nginx_na_80.png', 'Conflito de porta: 443 ocupada pelo dashboard do Wazuh e nginx na 80.'),
    ('07_cloudflare_dns_zabbix_e_monitoramento.png', 'Cloudflare: registros A zabbix e monitoramento para 174.129.199.16, em modo DNS only.'),
    ('08_security_group_g3-sc-wazuh.png', 'Security Group g3-sc-wazuh antes da restrição da 443.'),
    ('09_zabbix_acesso_https.png', 'Zabbix acessado por https://zabbix.maisplace.net.br, com certificado válido.'),
    ('10_wazuh_acesso_https_agentes_ativos.png', 'Wazuh acessado por https://monitoramento.maisplace.net.br, com os agentes ativos após a troca de porta.'),
    ('11_zabbix_system_information.png', 'Zabbix: System information com o servidor em execução (7.0.32).'),
    ('12_zabbix_hosts_zabbix_server.png', 'Zabbix: host Zabbix server cadastrado e disponível.'),
    ('13_zabbix_usuarios_guest_desativado.png', 'Zabbix: usuário guest desativado; apenas Admin ativo.'),
    ('14_depois_recursos_cpu_ram_swap_disco.png', 'Depois da instalação (29/10/2026, 17:07 UTC): 830 MB disponíveis e 935 MB de swap em uso.'),
    ('15_depois_portas_443_nginx_5601_8080_loopback.png', 'Depois: nginx na 443; dashboard do Wazuh (5601) e interface do Zabbix (8080) só em loopback.'),
    ('16_depois_servicos_versoes_agentes_vmstat.png', 'Depois: serviços ativos, versões, agentes e vmstat.'),
    ('17_sg_443_restrita_tela_de_edicao.png', 'Security Group: porta 443 restrita a endereço /32 (tela de edição).'),
]
for n, (f, cap) in enumerate(CAPS, 1):
    d.add_picture(PR + f, width=Cm(15))
    d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = d.add_paragraph('Figura 1.%d – %s' % (n, cap))
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].italic = True
    p.runs[0].font.size = Pt(9)
