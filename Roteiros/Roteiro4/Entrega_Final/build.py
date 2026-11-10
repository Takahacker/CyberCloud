from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
import sys

out = sys.argv[1]
d = Document()
for s in d.sections:
    s.left_margin = s.right_margin = Cm(2.5)
    s.top_margin = s.bottom_margin = Cm(2.5)
d.styles['Normal'].font.name = 'Calibri'
d.styles['Normal'].font.size = Pt(11)


def pend(t):
    p = d.add_paragraph()
    r = p.add_run('[PENDENTE] ' + t)
    r.bold = True
    r.font.color.rgb = RGBColor(0xB0, 0x30, 0x00)
    return p


def para(t):
    return d.add_paragraph(t)


def bul(t):
    return d.add_paragraph(t, style='List Bullet')


def tbl(rows):
    t = d.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    n = len(rows[0])
    lens = [max(min(len(r[j]), 90) for r in rows) + 6 for j in range(n)]
    tot = sum(lens)
    widths = [max(Cm(2.1), int(Cm(16) * l / tot)) for l in lens]
    for i, row in enumerate(rows):
        for j, c in enumerate(row):
            cell = t.cell(i, j)
            cell.width = widths[j]
            cell.text = ''
            r = cell.paragraphs[0].add_run(c)
            r.font.size = Pt(9.5)
            r.bold = (i == 0)
    d.add_paragraph()
    return t


# Capa
for _ in range(3):
    d.add_paragraph()
p = d.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('Insper – Engenharia\nCIBERSEGURANÇA EM NUVEM')
r.bold = True
r.font.size = Pt(16)
p = d.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('Roteiro 4 – Operação e gerenciamento: Zabbix')
r.bold = True
r.font.size = Pt(20)
d.add_paragraph()
for n in ['Eduardo Machado de Oliveira', 'Gustavo Eizo Takahashi', 'Henrique Leite dos Santos',
          'Lucas Kenji Kamikawa', 'Sidney Barbosa de Oliveira']:
    p = d.add_paragraph(n)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p = d.add_paragraph('Prof. Dr. Rodolfo Avelino')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p = d.add_paragraph('São Paulo, 10/11/2026')
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
d.add_page_break()

d.add_heading('Contexto do ambiente', 1)
para('O ambiente é o marketplace MaisPlace (maisplace.net.br), construído nos Roteiros 1 a 3: servidor web (Apache, WordPress), banco MySQL em sub-rede privada, Apache Guacamole como jump server, Cloudflare, Wazuh e CloudWatch. Neste roteiro foi acrescentado o Zabbix, instalado na mesma instância do Wazuh (g3-wazuh-server).')
para('Este documento segue a ordem das quatro tarefas do roteiro. Os horários aparecem em UTC ou no horário local (UTC-3), como indicado em cada caso.')

# Tarefa 1
d.add_heading('Tarefa 1 – Instalação e configuração do Zabbix', 1)
exec(open('t1_section.py', encoding='utf-8').read())

# Tarefa 2
d.add_heading('Tarefa 2 – Monitoramento dos servidores', 1)
d.add_heading('2.1 Banco de dados e jump server com Guacamole', 2)
para('Os hosts foram cadastrados no Zabbix 7.0.32 e monitorados pelo Zabbix agent 2 na porta 10050, a partir do Zabbix server (10.0.4.20).')
tbl([
    ['Host (Zabbix)', 'Instância AWS', 'IP privado', 'Rede', 'Templates'],
    ['db-01', 'g3-db-server-instance (t2.micro)', '10.0.136.239', 'Sub-rede privada, sem IP público', 'Linux by Zabbix agent; MySQL by Zabbix agent 2'],
    ['jump-01', 'guacamole (t3.micro)', '10.0.4.101', 'Sub-rede pública, acesso via Guacamole', 'Linux by Zabbix agent; Docker by Zabbix agent 2'],
    ['Zabbix server', 'g3-wazuh-server (t3.medium)', '10.0.4.20', 'zabbix.maisplace.net.br', 'Linux by Zabbix agent; Zabbix server health'],
])
para('Configuração aplicada:')
bul('Security Groups: porta 10050/tcp liberada para a VPC (10.0.0.0/16) nos grupos do banco e do Guacamole; SSH do banco restrito ao Security Group do Guacamole; SSH do servidor Zabbix liberado para o jump server.')
bul('Agentes: Server=127.0.0.1,10.0.0.0/16 e ServerActive=10.0.4.20 nos dois hosts.')
bul('MySQL: usuário dedicado de monitoramento (zbx_monitor) com apenas REPLICATION CLIENT, PROCESS, SHOW DATABASES e SHOW VIEW, sem acesso aos dados da aplicação. A senha foi informada por canal restrito e não consta neste documento. As macros {$MYSQL.DSN}, {$MYSQL.USER} e {$MYSQL.PASSWORD} foram definidas no host db-01.')
FIGS = 'evidencias_sidney/'
def fig(n, f, cap):
    d.add_picture(FIGS + f, width=Cm(15))
    d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = d.add_paragraph('Figura %s – %s' % (n, cap))
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].italic = True
    p.runs[0].font.size = Pt(9)
fig('2.1', '01_jump_terminal_agente_e_estado.png', 'jump-01 (ip-10-0-4-101): zabbix-agent2 ativo, containers do Guacamole em execução, HTTP 200 em 127.0.0.1:8080/guacamole/, memória e disco.')
fig('2.2', '02_db_terminal_agente_mysql_e_estado.png', 'db-01 (ip-10-0-136-239): zabbix-agent2 e mysql ativos; free -m com 123 MB disponíveis e sem swap; / com 68% de uso; uptime de 3h51 em 06/11/2026 (UTC).')
fig('2.3', '03_zabbix_hosts_cadastrados_ativos.png', 'Zabbix 7.0.32, Data collection > Hosts: db-01, jump-01 e Zabbix server habilitados, com disponibilidade ZBX em verde e os templates vinculados.')
fig('2.4', '04_db01_latest_data_recursos.png', 'Latest data de db-01: uso de CPU 0,6364%, CPU ociosa 99,36%, iowait, system e 1 vCPU.')
fig('2.5', '05_db01_mysql_disponibilidade_e_metricas.png', 'Latest data de db-01 (MySQL): eficiência do buffer pool 94,20%, utilização 18,90% e taxa de SELECT de 0,01667/s.')
fig('2.6', '06_jump01_latest_data_recursos.png', 'Latest data de jump-01: CPU ociosa 99,27% e consumo dos containers Docker.')
fig('2.7', '07_jump01_guacamole_checagem_operacional_e_docker.png', 'Latest data de jump-01 (Docker): container guacamole-guacamole-1 com CPU 0,2496%, 204,77 MB de memória, 32 PIDs e exit code 0.')
para('Checagem operacional do Guacamole: a verificação usa web.page.regexp[127.0.0.1,/guacamole/,8080,"guac",], que confirma que a página responde com o conteúdo esperado e não apenas que a porta está aberta. A coleta de containers pelo template Docker confirma o estado de guacamole, guacd e postgres.')
para('Conferência com o sistema operacional: na Figura 2.2 o terminal do db-01 mostra 123 MB de memória disponível e 68% da raiz em uso; o Zabbix mostrava, na última coleta antes da queda, 71,8% de uso da raiz (Figura 2.13). As capturas 2.4 a 2.7 são de latest data do Zabbix em 06/11/2026.')
para('Memória, disco e disponibilidade do agente dos dois hosts aparecem no dashboard (Figura 2.13). Em 06/11/2026 às 11:19, o jump-01 estava com 73,65% de memória usada e 27,86% da raiz; o db-01 estava com o agente indisponível desde 04:40 (seção 4.3).')

d.add_heading('Dashboard: indicadores por host', 3)
tbl([
    ['Host', 'Indicador', 'Chave do item', 'Widget sugerido'],
    ['db-01', 'Disponibilidade do agente', 'zabbix[host,agent,available]', 'Host availability'],
    ['db-01', 'Status do MySQL', 'mysql.ping', 'Item value (1 = Up)'],
    ['db-01', 'Eficiência do buffer pool', 'mysql.buffer_pool_efficiency', 'Gauge'],
    ['db-01', 'SELECT por segundo', 'mysql.queries.select.rate', 'Graph'],
    ['db-01', 'CPU e RAM disponível', 'system.cpu.util; vm.memory.available', 'Gauge/Graph; Item value'],
    ['jump-01', 'Disponibilidade do agente', 'zabbix[host,agent,available]', 'Host availability'],
    ['jump-01', 'Aplicação Guacamole (HTTP)', 'web.page.regexp[127.0.0.1,/guacamole/,8080,"guac",]', 'Item value'],
    ['jump-01', 'Containers Docker', 'docker.container_info[...]', 'Table'],
    ['jump-01', 'CPU, RAM e disco /', 'system.cpu.util; vm.memory.utilization; vfs.fs.dependent.size[/,pfree]', 'Graph; Progress bar'],
])

d.add_heading('2.2 Servidor Web e dashboard geral', 2)
para('Servidor web: instância EC2 t3.micro, IP privado 10.0.11.45, com Apache, PHP e WordPress. O acesso SSH só é possível a partir do Guacamole. O Zabbix agent 2 foi instalado nele e configurado com Server=127.0.0.1,10.0.4.20, ServerActive=10.0.4.20 e Hostname=web-01. No Security Group G3-sg-web-server foi adicionada a porta 10050/tcp com origem no Security Group do Zabbix server (g3-sc-wazuh).')
para('O host web-01 foi cadastrado com o template Linux by Zabbix agent active, nos grupos Linux servers e G3 - Servidores Web. Para a disponibilidade do Apache foram criados dois itens: proc.num[apache2] (processos em execução) e net.tcp.service[http,127.0.0.1,80] (resposta HTTP local). Eles não dependem do módulo mod_status, exigido pelo template Apache by Zabbix agent.')
para('Os servidores estão organizados em grupos por função: G3 - Banco de dados (db-01), G3 - Jump server (jump-01), G3 - Servidores Web (web-01) e G3 - Monitoramento (Zabbix server).')
d.add_picture('evidencias_lucas/L11_hosts_4_verdes.png', width=Cm(15)); d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
p = d.add_paragraph('Figura 2.8 – Data collection > Hosts em 10/11/2026: db-01, jump-01, web-01 e Zabbix server habilitados, com disponibilidade ZBX em verde.'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].italic = True; p.runs[0].font.size = Pt(9)
para('Coleta efetiva no web-01 (10/11/2026, 13:47, horário local): CPU 0,49%, memória usada 57,27%, disco da raiz 60,35%, 8 processos do Apache e porta 80 ativa (valor 1). A leitura do Apache é coerente com o site, que respondia HTTP 200 no mesmo período.')
d.add_picture('evidencias_lucas/L09_web01_latest.png', width=Cm(15)); d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
p = d.add_paragraph('Figura 2.9 – Monitoring > Latest data do web-01 em 10/11/2026: agente ativo disponível, Apache com porta 80 ativa e 8 processos, memória e CPU coletados há menos de 1 minuto.'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].italic = True; p.runs[0].font.size = Pt(9)
d.add_heading('Dashboard geral', 3)
para('Foi criado o dashboard "G3 - Visao geral (Roteiro 4)", com disponibilidade dos hosts, problemas por severidade, CPU, memória usada, disco da raiz, disponibilidade do agente e tráfego de rede de entrada e saída de cada servidor, além da disponibilidade do Apache e da lista de problemas atuais. Os blocos usam os itens system.cpu.util, vm.memory.util, vfs.fs.dependent.size[/,pused], zabbix[host,agent,available], net.if.in e net.if.out.')
d.add_picture('evidencias_lucas/L12_dashboard_geral.png', width=Cm(15)); d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
p = d.add_paragraph('Figura 2.10 – Dashboard em 10/11/2026, 13:46 (horário local): quatro hosts disponíveis e indicadores atuais do Zabbix server, db-01 e jump-01.'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].italic = True; p.runs[0].font.size = Pt(9)
d.add_picture('evidencias_lucas/L13_dashboard_rede.png', width=Cm(15)); d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
p = d.add_paragraph('Figura 2.11 – Dashboard: tráfego de rede de entrada e saída do Zabbix server, db-01 e jump-01 na última hora.'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].italic = True; p.runs[0].font.size = Pt(9)
d.add_picture('evidencias_lucas/L14_dashboard_web01.png', width=Cm(15)); d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
p = d.add_paragraph('Figura 2.12 – Dashboard: blocos do web-01 com CPU, memória, agente ativo, processos e porta do Apache, disco e tráfego de rede (10/11/2026, 13:47).'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].italic = True; p.runs[0].font.size = Pt(9)
d.add_picture('evidencias_lucas/L04_dashboard_g3.png', width=Cm(15)); d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
p = d.add_paragraph('Figura 2.13 – Dashboard durante o incidente de 06/11/2026, 11:19 (horário local): db-01 com o agente indisponível e os últimos valores congelados às 04:29 a 04:30 (CPU 100%).'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].italic = True; p.runs[0].font.size = Pt(9)

d.add_heading('Respostas da Tarefa 2', 3)
d.add_heading('Questão 1. Qual é a diferença entre o monitoramento realizado por meio de um agente instalado no servidor e o monitoramento utilizando o protocolo SNMP?', 4)
para('O agente (Zabbix agent 2) roda como serviço no próprio host e lê diretamente o kernel (/proc, /sys), logs, sockets e serviços locais, como o Docker, e plugins como o do MySQL. Pode coletar de forma passiva (o servidor consulta a porta 10050) ou ativa (o agente envia ao servidor pela 10051, com buffer local durante quedas de rede), e suporta TLS com PSK ou certificado. O SNMP (v1, v2c, v3) é um protocolo sem agente, pensado para roteadores, switches, nobreaks e outros equipamentos onde não se instala software. Os dados vêm de OIDs organizados em MIBs, sobre UDP 161 (consulta) e 162 (traps). As versões v1 e v2c enviam a community string sem cifrar; a v3 oferece autenticação e criptografia, mas é mais pesada e não expõe dados como containers ou métricas internas de bancos. Em servidores Linux na nuvem, o agente é a opção mais completa; o SNMP serve para equipamentos de rede.')
d.add_heading('Questão 2. Qual é a função dos templates no Zabbix e quais vantagens eles oferecem para o gerenciamento de múltiplos servidores?', 4)
para('Um template é um conjunto reutilizável de itens, triggers, gráficos, descoberta automática e macros para um tipo de sistema, como Linux by Zabbix agent ou MySQL by Zabbix agent 2. Ao vincular o template a um host, ele herda toda essa configuração sem precisar criá-la manualmente. Com vários servidores, isso traz padronização (todos medem e alertam da mesma forma), ganho de tempo (um servidor novo é monitorado ao receber o template), manutenção central (uma alteração no template vale para todos os hosts vinculados) e menos erro de configuração. Os valores que variam, como limites e credenciais, ficam em macros por host.')
para('No ambiente, os mesmos templates (Linux by Zabbix agent em todos os hosts, mais MySQL by Zabbix agent 2 no banco e Docker by Zabbix agent 2 no jump) deram a cada host entre 127 e 252 itens e cerca de 41 triggers sem configuração manual (Figura 2.3).')
d.add_heading('Questão 3. Um servidor pode estar disponível e, mesmo assim, a aplicação hospedada nele apresentar problemas de funcionamento? Como o Zabbix poderia identificar essa situação?', 4)
para('Um servidor pode estar disponível, ou seja, ligado, respondendo a ping e com o agente do Zabbix ativo, enquanto a aplicação está com problema: o Apache parado ou travado, erro 500 do WordPress, banco inacessível, certificado vencido ou página lenta. A disponibilidade do host não prova o funcionamento do serviço. Para identificar essa situação, monitora-se a camada da aplicação separadamente: estado do processo e da porta (net.tcp.service[http], proc.num[apache2]), checagem HTTP com código de resposta e conteúdo esperado (web.page.regexp ou um cenário Web), tempo de resposta e, no banco, mysql.ping. Cruzar o estado do host (verde) com o da aplicação (vermelho) mostra que o problema está no serviço e não na máquina.')
para('Caso observado no ambiente em 06/11/2026: o servidor web continuava ligado, com o agente do Wazuh ativo, e o Apache respondia, mas https://maisplace.net.br devolvia HTTP 500 com a mensagem "Error establishing a database connection" (Figura 2.14). A causa estava em outro servidor: o MySQL do db-01 caiu às 03:36 por falta de memória (seção 4.3). Uma checagem só de disponibilidade do servidor web ficaria verde; apenas uma checagem da aplicação (código HTTP e conteúdo da página) ou do MySQL mostra o problema.')
d.add_picture('evidencias_lucas/L05_site_erro_banco.png', width=Cm(12)); d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
p = d.add_paragraph('Figura 2.14 – https://maisplace.net.br em 06/11/2026, 11:20 (horário local): WordPress sem conexão com o banco (HTTP 500).'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].italic = True; p.runs[0].font.size = Pt(9)
d.add_heading('Questão 4. Considerando os recursos da organização, quais indicadores o grupo considera mais importantes para acompanhar a disponibilidade e o desempenho do ambiente? Justifique.', 4)
para('O grupo prioriza quatro grupos de indicadores:')
bul('Disponibilidade efetiva da aplicação: mysql.ping e conexões ativas, porque o WordPress depende do MySQL e a aplicação cai mesmo que a instância responda a ping; a resposta HTTP do Guacamole e o estado dos containers guacamole, guacd e postgres, já que o Guacamole é o único canal administrativo; e a porta 80/443 e os processos do Apache no servidor web.')
bul('Memória disponível e swap (vm.memory.available, system.swap.size[,pused]): as instâncias são pequenas, e a falta de memória faz o kernel encerrar processos como mysqld ou Java. No db-01 foi observada memória disponível de 123 MB, sem swap (Figura 2.2).')
bul('Espaço em disco (vfs.fs.dependent.size[/,pfree]): disco cheio impede escrita de logs e transações do MySQL. No db-01, a raiz estava com 68% de uso (Figura 2.2).')
bul('CPU, iowait e rede (system.cpu.util, iowait, net.if.in/out): ajudam a distinguir falta de capacidade de um possível ataque, como DoS ou mineração de criptomoeda, e iowait alto indica saturação do volume EBS.')

# Tarefa 3
d.add_heading('Tarefa 3 – Alertas e notificações', 1)
d.add_heading('3.1 Alertas configurados', 2)
para('Foram criadas sete triggers próprias do grupo (tag grupo = G3-roteiro4), além das triggers que vêm dos templates. Todas usam expressão de recuperação separada (histerese), para o alerta não oscilar perto do limite.')
tbl([
    ['Categoria', 'Host', 'Expressão', 'Severidade', 'Recuperação', 'Justificativa'],
    ['CPU', 'Zabbix server', 'min(/Zabbix server/system.cpu.util,3m)>80', 'Warning', 'max(...,2m)<60', 'Exige 3 min seguidos acima de 80%, ignorando picos curtos (como as rajadas do Wazuh).'],
    ['Memória', 'Zabbix server', 'max(/Zabbix server/vm.memory.size[available],5m)<300M', 'Average', 'min(...,5m)>500M', 'Instância com Wazuh e Zabbix, com cerca de 1 GB disponível em repouso; abaixo de 300 MB há risco de encerramento de processos.'],
    ['Memória', 'db-01', 'max(/db-01/vm.memory.size[available],5m)<150M', 'Average', 'min(...,5m)>250M', 'Host de 1 GB sem swap; o MySQL caiu por falta de memória em 06/11/2026.'],
    ['Disco', 'Zabbix server', 'last(/Zabbix server/vfs.fs.dependent.size[/,pused])>80', 'Warning', '<75', 'Folga para índices do Wazuh e histórico do Zabbix.'],
    ['Disco', 'db-01', 'last(/db-01/vfs.fs.dependent.size[/,pused])>80', 'Warning', '<75', 'Raiz já em 72%; disco cheio interrompe gravações do MySQL.'],
    ['Serviço', 'Zabbix server', 'max(/Zabbix server/zabbix[host,agent,available],2m)=0', 'High', 'last(...)=1', 'Serviço de coleta parado por 2 min.'],
    ['Serviço', 'web-01', 'max(/web-01/proc.num[apache2],2m)=0', 'High', 'last(...)>0', 'Sem processos do Apache por 2 min o site deixa de ser servido.'],
])
para('Para o serviço do banco também vale a trigger do template MySQL by Zabbix agent 2, "MySQL: Service is down" (High), que disparou de fato em 06/11/2026 às 03:36 (seção 4.3).')
d.add_heading('3.2 Testes de alerta e recuperação', 2)
exec(open('t3_testes.py', encoding='utf-8').read())
d.add_heading('3.3 Notificação por e-mail', 2)
para('O tipo de mídia Email foi configurado com smtp.gmail.com, porta 587, STARTTLS e autenticação com senha de aplicativo. O usuário Admin recebeu a mídia de destino e a ação "Report problems to Zabbix administrators" foi ativada. A senha não consta neste documento. A primeira tentativa, em 06/11/2026, falhou com "Login denied" porque a senha salva não era aceita pelo Gmail; depois da correção, o teste do tipo de mídia em 10/11/2026 retornou "Media type test successful".')
para('Teste do e-mail em 10/11/2026 (horário local): carga em dois vCPUs no Zabbix server das 13:38:24 às 13:43:24. O indicador system.cpu.util passou de 2,8% para 99,7% às 13:39 e ficou em 100% até 13:43.')
tbl([
    ['Evento', 'Horário (local)', 'E-mail recebido em lucaskenji49@gmail.com', 'Situação no Zabbix'],
    ['Problema (id 5549): G3 - CPU acima de 80% por 3 minutos em Zabbix server', '13:41:24', '13:41 – "Problem: G3 - CPU acima de 80% por 3 minutos em Zabbix server"', 'Sent'],
    ['Recuperação do mesmo problema', '13:46:24', '13:46 – "Resolved in 5m 0s: G3 - CPU acima de 80% por 3 minutos em Zabbix server"', 'Sent'],
])
d.add_picture('evidencias_lucas/L16_gmail_recebidos.png', width=Cm(15)); d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
p = d.add_paragraph('Figura 3.4 – Gmail: e-mails de problema (13:41) e de recuperação (13:46) gerados pelo evento de CPU de 10/11/2026.'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].italic = True; p.runs[0].font.size = Pt(9)
d.add_picture('evidencias_lucas/L15_action_log_enviado.png', width=Cm(15)); d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
p = d.add_paragraph('Figura 3.5 – Reports > Action log: registro de envio (status Sent) dos e-mails durante o mesmo teste, aqui para a trigger de CPU do template.'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].italic = True; p.runs[0].font.size = Pt(9)
para('Observação: o Wazuh tem e-mail habilitado para alertas de nível 7 ou mais, mas o envio continuava falhando em 10/11/2026 ("Error Sending email" no ossec.log), porque o wazuh-maild não faz autenticação no Gmail sem um relay local.')
d.add_heading('3.4 Respostas da Tarefa 3', 2)
d.add_heading('Questão 1. Qual é a diferença entre um indicador de monitoramento e uma condição de alerta (trigger)?', 3)
para('Um indicador (item) é a métrica coletada periodicamente, como o uso de CPU, o espaço livre em disco ou o código de resposta HTTP. Ele apenas registra o valor ao longo do tempo. A condição de alerta (trigger) é uma expressão lógica avaliada sobre os valores de um ou mais itens. Quando a expressão se torna verdadeira, a trigger passa ao estado PROBLEM, gera um evento e pode disparar ações de notificação.')
d.add_heading('Questão 2. Quais problemas podem ocorrer quando os limites de alerta são configurados de forma muito sensível ou pouco sensível?', 3)
para('Limites muito sensíveis geram muitos falsos positivos e levam à fadiga de alertas: a equipe passa a ignorar notificações, inclusive as reais. Limites pouco sensíveis geram falsos negativos: a degradação gradual, como memória ou disco enchendo, só é percebida depois que o serviço já caiu. O ajuste dos limites e do tempo de permanência da condição é o que equilibra os dois riscos. No ambiente, as rajadas do Wazuh chegam a 82% de CPU por pouco tempo; por isso a trigger de CPU exige 3 minutos seguidos acima de 80%. Já no db-01 o limite estava frouxo demais: não havia alerta de memória baixa, e a falta de memória só apareceu quando o MySQL já tinha caído.')
d.add_heading('Questão 3. Por que é importante monitorar a recuperação de um serviço, além de identificar sua indisponibilidade?', 3)
para('O evento de recuperação confirma que a ação corretiva funcionou e fecha o ciclo do incidente. Também permite medir a duração da degradação (MTTR) e comprovar o cumprimento de SLAs, e avisa a equipe de que pode encerrar o atendimento, evitando esforço duplicado. No teste 1 da seção 3.2, a CPU normalizou às 14:26 UTC, mas o problema só foi fechado às 14:31, quando a coleta voltou: a recuperação também depende de dados chegando, e um alerta que não fecha é sinal de coleta interrompida.')
d.add_heading('Questão 4. O recebimento de um alerta significa necessariamente que ocorreu um incidente de segurança? Justifique.', 3)
para('Não. A maioria dos alertas vem de eventos rotineiros, como pico de CPU durante um backup, disco cheio por falta de rotação de logs ou indisponibilidade durante uma atualização. Mas métricas de infraestrutura podem ser o primeiro sinal de um ataque: CPU em 100% pode indicar mineração de criptomoeda ou DoS, e crescimento súbito de disco ou memória pode vir de um ataque de força bruta gerando logs ou de um ransomware cifrando arquivos. Por isso os alertas do Zabbix precisam ser avaliados junto com os eventos do Wazuh.')
d.add_heading('Questão 5. Quais seriam as consequências para a operação da organização caso os alertas fossem gerados corretamente, mas não houvesse um processo definido para seu tratamento?', 3)
para('Alertas sem processo definido dão uma falsa sensação de controle. As consequências são aumento do tempo de reparo (sem procedimento a equipe improvisa), falta de responsável (sem escalonamento ninguém assume o alerta) e prejuízos financeiros e de conformidade, como indisponibilidade de receita, descumprimento de SLA e de prazos de comunicação de incidentes previstos na LGPD. Foi exatamente o que aconteceu em 06/11/2026: o Zabbix abriu "MySQL: Service is down" às 03:36 e o Wazuh registrou alertas de nível 12, mas não havia ação de notificação no Zabbix e o e-mail do Wazuh estava falhando; às 11:20 o site ainda mostrava erro de banco.')

# Tarefa 4
d.add_heading('Tarefa 4 – Comparação entre Zabbix e Wazuh', 1)
d.add_heading('4.1 Método e limites desta análise', 2)
para('A comparação separa três categorias de afirmação, para não atribuir a uma ferramenta algo que ela não coletou:')
bul('Capacidade da ferramenta: o que o produto oferece na documentação (Zabbix 7.0 e Wazuh 4.9.2, as versões instaladas pelo grupo). Não significa que esteja habilitado no ambiente.')
bul('Observado no ambiente: o que o grupo efetivamente viu nos dois painéis, com captura, host e horário.')
bul('Recomendação: melhoria proposta pelo grupo, ainda não implementada.')
para('Estado do ambiente conforme registrado na Tarefa 1: Zabbix 7.0.32 (servidor, frontend e agent2) com MySQL 8.4 e nginx, na mesma instância t3.medium (2 vCPU, 4 GiB) do Wazuh 4.9.2 (manager, indexer e dashboard). O Wazuh já recebia os eventos dos servidores web e de banco como agentes e os logs do CloudWatch (Roteiros 1 e 3).')
para('Hosts no Zabbix em 10/11/2026 (Figura 2.8): Zabbix server, db-01, jump-01 e web-01, todos disponíveis.')
para('Cobertura em 10/11/2026: o Wazuh tem agentes em web-server (001, grupo web) e db-server (002, grupo default), na versão 4.9.0, marcados como desatualizados em relação ao manager 4.9.2. O jump-01 não tem agente do Wazuh. Servidor web e banco aparecem nas duas plataformas.')

d.add_heading('4.2 Matriz comparativa', 2)
tbl([
    ['Aspecto', 'Zabbix', 'Wazuh', 'Habilitado no ambiente?'],
    ['Objetivo principal', 'Disponibilidade, desempenho e capacidade', 'Detecção de ameaças, integridade e conformidade (SIEM/XDR)', 'Ambos instalados; uso efetivo depende das Tarefas 2 e 3'],
    ['Tipo de dado', 'Métricas numéricas periódicas (CPU, RAM, disco, rede, estado de serviços)', 'Eventos e logs (autenticação, syslog, Apache, FIM, inventário, vulnerabilidades)', 'Wazuh: logs dos servidores e do CloudWatch (Roteiros 1 e 3). Zabbix: ver Tarefa 2'],
    ['Coleta', 'Agente (passivo/ativo), SNMP, IPMI, JMX, HTTP, checagens simples', 'Agente em cada host, syslog remoto e integrações com nuvem', 'Agentes nos dois casos'],
    ['Detecção', 'Triggers por limiar e expressões sobre séries temporais', 'Regras e decodificadores sobre eventos, correlação, MITRE ATT&CK', 'Regras padrão do Wazuh; triggers do Zabbix criadas na Tarefa 3'],
    ['Integridade de arquivos', 'Item de checksum, por exemplo vfs.file.cksum[/etc/passwd] do template Linux, com trigger de alteração', 'FIM nativo (syscheck), com tempo real', 'Ambos ativos: no Zabbix, checksum de /etc/passwd; no Wazuh, syscheck a cada 12 h em /etc, /usr/bin, /usr/sbin, /bin, /sbin e /boot, e FIM em tempo real de /var/www/html no grupo web'],
    ['Vulnerabilidades', 'Não é seu foco (só detecta alteração na lista de pacotes)', 'Inventário de pacotes e correlação com CVE; SCA (avaliação de configuração)', 'Vulnerability Detection ativo (feed a cada 60 min); SCA de hora em hora no grupo web. O Zabbix gerou "Number of installed packages has been changed" e o Wazuh registrou os eventos dpkg da mesma instalação (seção 4.3)'],
    ['Resposta ativa', 'Scripts/ações em eventos, sem foco em segurança', 'Active Response (bloquear IP, executar comando)', 'O bloqueio automático do ambiente é feito por Fail2ban + API da Cloudflare, não pelo Wazuh'],
    ['Alertas', 'Notificação por e-mail, webhook e mensagens, com escalonamento', 'Alertas no dashboard e e-mail nativo (wazuh-maild) a partir de um nível', 'Wazuh: e-mail ativo para nível 7 ou mais, via smtp.gmail.com, mas falhando ("Error Sending email" no ossec.log em 06/11/2026); o wazuh-maild não autentica no Gmail sem um relay local. Zabbix: ver Tarefa 3'],
    ['Histórico e tendência', 'Gráficos, histórico e tendência por item', 'Busca e filtragem de eventos no indexer', 'Ambos'],
    ['Recurso consumido', 'Servidor, banco MySQL e frontend', 'Manager, indexer (Java, maior consumo de RAM) e dashboard', 'Medido na Tarefa 1 (antes e depois)'],
])

d.add_heading('4.3 Comparação do mesmo servidor em intervalo identificado', 2)
para('Alvo: servidor de banco de dados (db-01 no Zabbix, db-server no Wazuh, agente 002, IP 10.0.136.239). Intervalo: 06/11/2026, 03:00 a 05:30, no horário local exibido pelas duas interfaces (UTC-3). O banco foi escolhido por estar nas duas plataformas e por ter sofrido um incidente real no período, o que permite comparar o mesmo evento.')
tbl([
    ['Momento (06/11/2026)', 'Zabbix (db-01)', 'Wazuh (db-server)', 'Semelhança ou diferença'],
    ['03:36', 'High: MySQL: Service is down. Average: Linux: Load average is too high (per CPU load over 1.5 for 5m).', '03:36:22 (um segundo depois): regra 5108, nível 12, "System running out of memory. Availability of the system is in risk.", mais dois "Apparmor DENIED" (52002). Antes, às 03:29:46 a 03:29:55, uma rajada de eventos de pacotes dpkg (regras 2902 e 2904, nível 7).', 'Mesmo instante nas duas ferramentas. O Zabbix mostra o efeito (MySQL parou, carga alta); o Wazuh mostra a causa provável (falta de memória). Os eventos de dpkg às 03:29 indicam instalação de pacotes pouco antes, que não aparece como alerta no Zabbix nesse horário.'],
    ['04:09', 'Warning: Linux: Number of installed packages has been changed.', 'Pico de 17 e 21 eventos de 04:05 a 04:15: "New dpkg (Debian Package) installed" (regra 2902) e "Dpkg half configured" (2904), nível 7, até 04:11:45, intercalados com falta de memória (5108) às 04:10:55 e 04:11:41.', 'Mesmo fato visto de dois jeitos: o Zabbix só sabe que a contagem de pacotes mudou; o Wazuh mostra cada pacote instalado e que a instalação ocorreu com o sistema sem memória.'],
    ['04:29 a 04:35', 'Sem alerta de memória no Zabbix nessa lista de problemas.', 'Level 12, regra 5108: "System running out of memory. Availability of the system is in risk." em db-server (04:29:26, 04:30:20, 04:35:34), junto com "Apparmor DENIED" (regra 52002, nível 3).', 'Informação específica do Wazuh: a causa provável em nível de sistema. O Zabbix só tem o item de memória disponível (419 MB na última coleta) e não gerou trigger.'],
    ['04:40', 'Average: Linux: Zabbix agent is not available (for 3m).', 'Regra 504, nível 3, "Wazuh agent disconnected." em db-server, às 05:01:32.', 'Os dois detectam a perda do agente, com diferença de cerca de 21 min entre os horários (cada ferramenta tem sua própria tolerância).'],
])
fig4 = 'evidencias_lucas/'
d.add_picture(fig4 + 'L01_zabbix_problems_db01.png', width=Cm(15)); d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
p = d.add_paragraph('Figura 4.1 – Zabbix, Monitoring > Problems: alertas do db-01 em 06/11/2026 (agente indisponível às 04:40:05, pacotes alterados às 04:09:38). Capturada com sessão Admin em 06/11/2026.'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].italic = True; p.runs[0].font.size = Pt(9)
d.add_picture(fig4 + 'L02_wazuh_events_db-server.png', width=Cm(15)); d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
p = d.add_paragraph('Figura 4.2 – Wazuh, Threat Hunting > Events do agente db-server (002), 06/11/2026 das 03:00 às 05:30: 91 eventos, e a última linha é a desconexão do agente às 05:01:32.'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].italic = True; p.runs[0].font.size = Pt(9)
d.add_picture(fig4 + 'L03_wazuh_db-server_0320_0345.png', width=Cm(15)); d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
p = d.add_paragraph('Figura 4.3 – Wazuh, Events do db-server de 03:20 a 03:45 (06/11/2026): rajada de eventos dpkg às 03:29 e, às 03:36:22, falta de memória (regra 5108) e AppArmor DENIED.'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].italic = True; p.runs[0].font.size = Pt(9)
para('Depois da perda do agente às 04:40, o Zabbix manteve no painel os últimos valores do db-01 (CPU 100%, com 92,65% de tempo de sistema, sinal de que o kernel estava ocupado tentando liberar memória) sem atualização. Quem lê só o painel pode tomar um valor velho como atual; o indicador de disponibilidade do agente é o que mostra que os dados pararam.')
para('Leitura dos dados (observada nas duas ferramentas): o mesmo incidente no db-01 aparece no Zabbix como problemas de serviço, carga e disponibilidade do agente, e no Wazuh como eventos de falta de memória, negações do AppArmor e desconexão do agente. Os horários dos dois lados são coerentes entre 03:25 e 05:01. O Wazuh também registrou "System running out of memory" no servidor de monitoramento (ip-10-0-4-20, 04:33:48), o mesmo que hospeda o Zabbix. O Wazuh registrou a falta de memória do db-server às 03:36:22, um segundo depois do alerta de MySQL fora do ar no Zabbix (03:36:21), o que sustenta a falta de memória como causa; o Zabbix, sozinho, não mostrava essa causa. A causa final (qual processo consumiu a memória) não foi investigada nos logs do servidor.')

d.add_heading('4.4 Limitações observadas e melhorias propostas', 2)
para('Observado (medições da Tarefa 1 e do próprio ambiente em 06/11/2026):')
bul('As duas plataformas compartilham uma instância de 4 GiB. Antes do Zabbix havia cerca de 1,1 GB de RAM disponível e foi necessário criar swap de 2 GB; o indexer do Wazuh é o maior consumidor de memória.')
bul('O Wazuh tem rajadas de CPU e I/O (o wazuh-modulesd chegou a 81,8% de CPU após o boot), que distorcem medições se a condição não for controlada.')
bul('A porta 443 foi dividida por nome com nginx; durante a troca o Wazuh ficou indisponível por 1 a 2 minutos.')
bul('No db-01 (t2.micro, 1 vCPU) havia 123 MB de memória disponível, sem swap, e 68% da raiz em uso (Figura 2.2). A coleta do agente e do plugin do MySQL soma carga a um host já justo em memória.')
bul('Zabbix e Wazuh estão na mesma instância: se ela falhar, o grupo perde monitoramento operacional e de segurança ao mesmo tempo.')
bul('Lacuna de cobertura: o jump-01 não tem agente do Wazuh. Além disso, o Zabbix não consegue testar o site pelo endereço público, porque o WAF da Cloudflare bloqueia o IP da instância, que fica nos EUA.')
bul('Agentes do Wazuh desatualizados (4.9.0) em relação ao manager (4.9.2).')
bul('Alertas sem entrega: o db-01 ficou sem MySQL desde 03:36 e o site exibia erro de banco às 11:20, cerca de 8 horas depois, sem que ninguém fosse avisado. Na época, o Zabbix não tinha notificação funcionando e o e-mail do Wazuh estava falhando; a notificação do Zabbix só foi comprovada em 10/11/2026.')
bul('Antes deste roteiro não havia trigger de memória baixa no db-01; o Zabbix viu o efeito (MySQL fora, carga alta) mas não a causa. A trigger foi criada na Tarefa 3.')
bul('Tempos de detecção diferentes para a mesma perda de agente: 04:40 no Zabbix e 05:01 no Wazuh.')
bul('Falha recorrente no db-01: o MySQL ficou fora do ar por 1 dia, 8 h e 46 min (06/11, 03:36, a 07/11, 12:23) e novamente por 10 h e 15 min em 09/11 (Figura 3.3). Em 10/11 o agente do Zabbix caiu pelo menos oito vezes e o sistema travou (status check da instância reprovado), até um reboot por volta das 13:10 (horário local) restabelecer o banco e o site. O host de 1 GB sem swap não sustenta a carga atual.')
para('Recomendações (não implementadas):')
bul('Disponibilidade: separar Zabbix e Wazuh em instâncias distintas ou manter uma verificação externa; backup do banco do Zabbix e dos dados do Wazuh; monitorar a própria instância com o CloudWatch.')
bul('Desempenho: aumentar a memória da instância ou limitar o heap do indexer; ajustar a retenção de histórico do Zabbix e dos índices do Wazuh; não depender de swap.')
bul('Segurança: restringir as interfaces por IP ou VPN; usuários nominais e autenticação em dois fatores no Zabbix (hoje só existe Admin); TLS entre agentes e servidor; enviar os alertas do Wazuh ao mesmo canal de e-mail do Zabbix; fechar a porta 80 se o certificado puder ser validado por DNS.')

d.add_heading('4.5 Respostas às questões da Tarefa 4', 2)
d.add_heading('Questão 1. Quais são as principais diferenças entre o monitoramento operacional realizado pelo Zabbix e o monitoramento de segurança realizado pelo Wazuh?', 3)
para('O monitoramento operacional pergunta se o serviço está disponível e com desempenho adequado: o host responde, Apache e MySQL estão ativos, CPU, memória e disco têm folga. O monitoramento de segurança pergunta se há atividade indevida ou risco: tentativas de login, alteração de arquivos, exploração de vulnerabilidades, comportamento anômalo. O Zabbix é a ferramenta operacional do grupo, baseada em métricas e limiares. O Wazuh é a ferramenta de segurança, baseada em eventos e regras. Elas se sobrepõem em parte: um pico de CPU pode ser carga legítima ou mineração de criptomoeda, e um serviço parado pode ser falha ou ataque. Por isso uma não substitui a outra.')
d.add_heading('Questão 2. Em quais situações as duas plataformas podem identificar informações relacionadas a um mesmo evento? Apresente um exemplo.', 3)
para('Para o evento escolhido na seção 4.3, o Zabbix informa o que mudou no estado do servidor: valor do item, momento em que o limiar foi cruzado, duração, severidade da trigger e recuperação. O Wazuh informa o que ocorreu no sistema: o registro de log original, o decodificador e a regra acionados, o nível, o agente e a origem do evento. As duas mostram host, horário e o fato de que algo aconteceu; o Zabbix acrescenta a série numérica e a tendência, o Wazuh acrescenta o contexto e o conteúdo do evento.')
para('No caso observado (seção 4.3): o Zabbix mostrou, para o MySQL, horário (03:36:21), severidade High, nome do problema, duração, status PROBLEM e tags (class: database, component: application); o Wazuh mostrou, no mesmo segundo, timestamp (03:36:22), agent.name db-server, rule.id 5108, rule.level 12 e a descrição "System running out of memory". Só o Zabbix diz que o serviço parou; só o Wazuh diz que o sistema ficou sem memória.')
d.add_heading('Questão 3. Qual é a diferença entre identificar uma indisponibilidade de serviço e identificar a causa dessa indisponibilidade?', 3)
para('Identificar a indisponibilidade é saber que o serviço parou, desde quando e com que impacto; identificar a causa é saber por que ele parou. A primeira pergunta é respondida por checagens de estado e limiares; a segunda exige contexto: logs, eventos do sistema e o que mudou antes da falha. O Zabbix detecta e dimensiona a indisponibilidade: indica que o host ou o serviço deixou de responder, desde quando, e mostra o que acontecia antes (CPU, memória, disco, rede). O Wazuh ajuda a explicar a causa: logs do sistema e da aplicação no momento da falha (erro do Apache ou do MySQL, encerramento por falta de memória, falha de autenticação, alteração de configuração), que mostram se foi recurso esgotado, erro operacional ou ataque. A causa raiz costuma exigir cruzar os dois: o Zabbix marca o início do problema e o Wazuh contém os eventos daquele intervalo. Se o agente de uma das plataformas estiver parado, essa visão se perde, o que justifica uma verificação externa. No incidente observado no db-01 em 06/11/2026 (seção 4.3), o Zabbix registrou MySQL fora do ar às 03:36 e perda do agente às 04:40, enquanto o Wazuh registrou falta de memória do sistema entre 04:29 e 04:35 e a desconexão do agente às 05:01. O Wazuh registrou a falta de memória às 03:36:22, um segundo depois do alerta de MySQL fora do ar no Zabbix (03:36:21), o que aponta a falta de memória como causa.')
d.add_heading('Questão 4. Considerando os resultados dos testes realizados, quais limitações foram identificadas no monitoramento implementado pelo grupo?', 3)
para('As limitações observadas até agora estão na seção 4.4: concentração das duas plataformas em uma só instância com pouca folga de memória, necessidade de swap, rajadas de CPU e I/O do Wazuh, indisponibilidade breve do Wazuh na troca da porta 443 e ausência de usuários nominais no Zabbix.')
para('Nos testes da Tarefa 3, a trigger de CPU disparou cerca de 3 minutos depois do início da carga (14:19:33 → 14:22:24 UTC), porque exige três coletas acima de 80% com intervalo de 1 minuto, e só fechou quando voltaram a chegar dados (14:31:30). O agente parado gerou alerta 3 minutos depois da parada. Isso é intencional, mas significa que picos curtos não geram alerta. A notificação por e-mail do Zabbix só funcionou depois da correção da senha (seção 3.3).')
d.add_heading('Questão 5. Como as informações produzidas pelas duas plataformas poderiam apoiar o trabalho de um Centro de Operações de Rede (NOC) e de um Centro de Operações de Segurança (SOC)?', 3)
para('O NOC cuida da disponibilidade e do desempenho; seu insumo é o Zabbix, com painéis de estado, alertas por limiar e histórico para planejamento de capacidade. O SOC cuida de detectar, investigar e responder a ameaças; seu insumo é o Wazuh, com eventos correlacionados, alertas de segurança e inventário de vulnerabilidades. Os dois times se complementam: o NOC aciona o SOC quando um problema operacional tem sinais de ataque, e o SOC aciona o NOC quando um incidente de segurança afeta a disponibilidade. Para um grupo pequeno como o nosso, as duas plataformas formam uma visão única de operação e segurança, com os alertas indo aos mesmos responsáveis.')

d.add_heading('Conclusões', 1)
para('Zabbix e Wazuh coexistem na mesma instância, com HTTPS por subdomínio e acesso restrito por IP, mas a memória é o limite do ambiente: a instância de monitoramento opera com swap e registrou alerta de falta de memória.')
para('O incidente real de 06/11/2026 mostrou o valor das duas ferramentas juntas: o Zabbix detectou o efeito (MySQL fora do ar, carga alta, agente perdido) e o Wazuh registrou a causa provável (falta de memória no db-server) no mesmo segundo. Mostrou também a principal falha do ambiente: os alertas existiam, mas ninguém foi avisado, e o site ficou fora do ar por horas.')
para('Prioridades: entregar também os alertas do Wazuh (relay de e-mail), aumentar memória ou criar swap no db-01, completar a cobertura (agente do Wazuh no jump-01) e separar ou ampliar a instância de monitoramento.')

d.save(out)
