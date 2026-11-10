para('Os dois testes foram feitos no host Zabbix server (g3-wazuh-server) em 06/11/2026, por ser o único servidor com acesso SSH disponível ao grupo naquele momento. Horários em UTC; a interface do Zabbix mostra o horário local (UTC-3).')
tbl([
    ['Teste', 'Condição provocada', 'Indicador e valores', 'Alerta', 'Recuperação'],
    ['1. Carga de CPU', 'Dois processos "yes" (um por vCPU) por 5 min, de 14:19:33 a 14:24:33', 'system.cpu.util: 4,1% (14:19) → 85,2% (14:20) → 100% (14:21 a 14:24) → 19,1% (14:25) → 2,6% (14:26)', '14:22:24 – "G3 - CPU acima de 80% por 3 minutos", Warning', '14:31:30 – RESOLVED (duração 9 min 6 s; ver observação)'],
    ['2. Serviço parado', 'systemctl stop zabbix-agent2 às 14:27:21; reinício automático às 14:30:51', 'zabbix[host,agent,available]: 1 até 14:27:26; 0 em 14:28:26, 14:29:26 e 14:30:26; erro "Connection refused" na porta 10050', '14:30:26 – "G3 - Agente do Zabbix sem resposta por 2 minutos", High', '14:31:26 – RESOLVED (duração 1 min)'],
])
para('Observação sobre o teste 1: a CPU já estava normal às 14:26, mas a recuperação só foi registrada às 14:31:30. Como o teste 2 parou o agente às 14:27:21, não chegaram novos valores de CPU, e a trigger, que só é reavaliada quando chega um valor novo, ficou em PROBLEM até o agente voltar. Isso mostra, na prática, que um alerta pode ficar aberto ou desatualizado quando a coleta para.')
d.add_picture('evidencias_lucas/L06_t3_cpu_problem.png', width=Cm(15)); d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
p = d.add_paragraph('Figura 3.1 – Problema de CPU aberto às 11:22:24 (horário local) no Zabbix server, com a tag grupo: G3-roteiro4.'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].italic = True; p.runs[0].font.size = Pt(9)
d.add_picture('evidencias_lucas/L07_t3_historico_resolvidos.png', width=Cm(15)); d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
p = d.add_paragraph('Figura 3.2 – Histórico de problemas: os dois alertas de teste resolvidos (agente: 11:30:26 a 11:31:26; CPU: 11:22:24 a 11:31:30, horário local).'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].italic = True; p.runs[0].font.size = Pt(9)
para('Ambiente restaurado: a carga terminou sozinha (timeout de 5 min) e o zabbix-agent2 voltou a responder às 14:31 UTC, com a CPU em 2,6%.')

d.add_heading('Serviço indisponível: caso real do MySQL', 3)
para('Além dos testes controlados, o alerta de serviço indisponível do roteiro foi comprovado por um evento real no db-01. O Zabbix abriu "MySQL: Service is down" (High) e registrou a recuperação de cada ocorrência (Figura 3.3): 06/11, 00:08:31 a 00:21:10; 06/11, 03:36:21 a 07/11, 12:23:10; e 09/11, 04:46:54 a 15:02:35 (horário local). Depois do reboot de 10/11, o item mysql.ping voltou a 1.')
d.add_picture('evidencias_lucas/L08_t3_mysql_down_resolved.png', width=Cm(15)); d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
p = d.add_paragraph('Figura 3.3 – Zabbix, Problems (histórico de 7 dias) do db-01: as três ocorrências de "MySQL: Service is down", todas com recuperação registrada.'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.runs[0].italic = True; p.runs[0].font.size = Pt(9)
