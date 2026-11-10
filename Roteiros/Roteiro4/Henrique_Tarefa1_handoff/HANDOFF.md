# Handoff - Roteiro 4 (Zabbix), Tarefa 1 - Henrique

Disciplina: Cibersegurança em Nuvem (Prof. Rodolfo Avelino). Grupo G3.
Frente: Tarefa 1 (T1 Q1 a Q4): Zabbix e Wazuh na mesma instância, DNS na Cloudflare, HTTPS, acesso restrito, comparativo de recursos.
Data da execução: 29/10/2026. Horários de terminal em UTC; prints de navegador em horário local (UTC-3).

Status: instalação, DNS, HTTPS com redirecionamento, restrição da 443 a um IP, medição "depois" e rascunho do texto com as respostas Q1 a Q4 (texto_tarefa1.md) concluídos. A Tarefa 1 só fecha depois da revisão do texto pelo autor e da liberação da 443 para os demais IPs: ver seção 6. Principal risco levantado: RAM no limite (830 MB disponíveis e 935 MB em swap), ver seção 5.

## 1. Estado atual

- Zabbix 7.0.32 (server, frontend, agent2) instalado na mesma instância do Wazuh, com MySQL 8.4.11 e nginx 1.28.3.
- Zabbix: https://zabbix.maisplace.net.br (certificado Let's Encrypt).
- Wazuh: https://monitoramento.maisplace.net.br (agora atrás do nginx, com o mesmo certificado). Os agentes web-server e db-server continuaram Active (Agents Active 2, Disconnected 0 no dashboard, depois da troca de porta).
- Zabbix: 1 host (Zabbix server), 356 templates, 153 itens (141 ativos, 12 not supported), 83 triggers, 0 problemas.
- Usuário guest do Zabbix desativado (grupos Disabled, Guests, Internal). Só existem Admin e guest; nenhum usuário nominal foi criado ainda.

## 2. Ambiente

| Item | Valor |
|---|---|
| Instância | g3-wazuh-server, i-0363e594868beaee8, t3.medium (2 vCPU, 4 GiB) |
| IPs | privado 10.0.4.20, público 174.129.199.16 (Elastic IP g3-wazuh-eip) |
| SO | Ubuntu 26.04.1 LTS, kernel 7.0.0-1014-aws |
| Disco | volume EBS vol-0f280749333e7f0d3, /dev/sda1, 120 GiB (116G no df), Encrypted: No (visto no console; esse print não entrou no pacote) |
| Wazuh | manager, indexer e dashboard 4.9.2-1; filebeat 7.10.2; heap do indexer 1024m |
| Zabbix | 7.0.32 (zabbix-release 7.0-5, pacotes 1:7.0.32-2+ubuntu26.04) |
| Banco | MySQL 8.4.11, escutando só em 127.0.0.1 |
| Web | nginx 1.28.3, PHP 8.5.4 (php8.5-fpm, pool do Zabbix em /run/php/zabbix.sock) |
| Certificado | Let's Encrypt, SAN zabbix e monitoramento, válido de 29/10/2026 a 27/01/2027, renovação por certbot.timer |
| DNS | Cloudflare, zona maisplace.net.br: zabbix e monitoramento são A para 174.129.199.16, DNS only |
| Security Group | g3-sc-wazuh (sg-037a90ce974392b5e) |

Acesso SSH: chave ~/.ssh/g3-cybercloud/g3-wazuh-key.pem, usuário ubuntu, IP 174.129.199.16. A porta 22 só aceita 3 IPs /32 do Security Group; se o seu IP não estiver nela, peça para incluir.
Atenção: o Ubuntu 26.04 usa sudo-rs. O usuário ubuntu tem sudo sem senha, mas "sudo -v" pede senha e falha. Não use "sudo -v".

## 3. O que foi feito, em ordem

1. Medição "antes" (sem swap, antes de instalar o Zabbix), 15:48 UTC.
2. Swap de 2 GB persistente e vm.swappiness=10, por segurança (RAM disponível ~1,1 GB e sem swap). Ver configs/swap-e-sysctl.txt.
3. Repositório oficial do Zabbix 7.0 para Ubuntu 26.04 e instalação de zabbix-server-mysql, zabbix-frontend-php, zabbix-nginx-conf, zabbix-sql-scripts, zabbix-agent2, mysql-server e nginx. Dependências relevantes: php8.5-fpm e snmpd. Nenhum pacote do Wazuh foi alterado.
4. MySQL limitado em memória (pool de 256 MB, performance_schema e binlog desligados): configs/mysql-zz-zabbix.cnf. Banco "zabbix" e usuário "zabbix"@"localhost" criados; schema importado (203 tabelas, 45 s). Senha gerada aleatoriamente, gravada em zabbix_server.conf e em ~/zabbix_db_pass.txt (modo 600).
5. Frontend do Zabbix no nginx só em loopback (127.0.0.1:8080): configs/zabbix-nginx-package-linhas-1-a-3.conf. Site default do nginx removido.
6. DNS: registro A "zabbix" criado na Cloudflare, DNS only (print 07).
7. Porta 80 liberada no Security Group (0.0.0.0/0), bloco nginx de validação ACME (configs/00-acme.conf) e certificado emitido com certbot (webroot, um certificado para os 2 nomes).
8. Corte da 443: dashboard do Wazuh movido para 127.0.0.1:5601 (configs/wazuh-dashboard-opensearch_dashboards.yml-diff.txt) e nginx assumiu a 443 com dois server blocks por nome: configs/10-zabbix-tls.conf e configs/11-wazuh-tls.conf. O Wazuh ficou fora do ar por cerca de 1 a 2 minutos.
9. Assistente web do Zabbix concluído (nome ZBX-G3, fuso America/Sao_Paulo) e guest desativado.
10. Redirecionamento HTTP para HTTPS na porta 80, preservando o caminho do desafio ACME (configs/00-acme.conf).
11. Porta 443 do Security Group restringida ao IP do Henrique (177.9.102.219/32), em substituição à regra 0.0.0.0/0.

Validação feita de fora da instância: os dois nomes respondem 302 (setup.php e /app/login) com certificado verificado, e a página de login do Wazuh carrega.
Redirecionamento testado de fora (29/10/2026, ~14:20 local): http://zabbix... e http://monitoramento... respondem 301 para https com o mesmo caminho e query string; /.well-known/acme-challenge/ não redireciona; https://zabbix responde 200 e https://monitoramento responde 302, com certificado verificado.

## 4. Decisões e motivos

- DNS only nos dois subdomínios (decisão do Henrique). O Roteiro 4 não define proxied ou DNS only. O passo a passo do Roteiro 1 anota que o tráfego dos agentes do Wazuh (1514/1515) não passa pelo proxy da Cloudflare, e "monitoramento" já era DNS only. NÃO foi verificado se os agentes usam esse nome como endereço do manager (conferir com: sudo grep -A4 '<server>' /var/ossec/etc/ossec.conf nos hosts web e db). Como "monitoramento" já expõe o mesmo IP, proxiar o "zabbix" não esconderia nada.
- Let's Encrypt (HTTP-01) em vez de Cloudflare Origin Certificate, porque o registro é DNS only. Consequência: a porta 80 precisa ficar aberta ao mundo para validar e renovar.
- Cloudflare Access não se aplica (exige proxied). O acesso restrito fica por conta do Security Group e do login das plataformas.
- Zabbix em loopback com proxy reverso, em vez de direto na 443, para não alterar o arquivo gerenciado pelo pacote e separar os sites por nome.
- Swap de 2 GB e tuning do MySQL, porque a instância tinha ~1,1 GB de RAM disponível sem swap.

## 5. Medições

Antes (sem swap, Wazuh estável), 29/10/2026 15:48:44 UTC, uptime 1h06, 3 agentes Active (prints 02 e 03):

| Métrica | Valor |
|---|---|
| vCPU | 2 (Intel Xeon Platinum 8259CL) |
| CPU instantânea (top, 2a amostra) | 1,8% us, 0,6% sy, 97,6% idle, 0,0% wa |
| vmstat (após a 1a linha) | idle ~97 a 98% |
| Load average 1/5/15 min | 0,01 / 0,49 / 0,92 |
| RAM total / usada / disponível | 3831 / 2711 / 1120 MB |
| Swap | 0 |
| Disco / | 19G usados de 116G (17%) |
| Maior consumo de RAM | wazuh-indexer (java), RSS 1.484.004 KB (37,8%) |

Swap criado depois da medição acima. Print 04 (16:13:54 UTC): swap 2G, 251,9M em uso, RAM disponível 1055 MB, swappiness 10.

Aviso para a comparação: o Wazuh tem rajadas. Em coletas anteriores à baseline, com uptime menor, o wazuh-modulesd chegou a 81,8% (top, 15:25 UTC) e 61,1% (top, 15:30 UTC) de CPU, com iowait de 19 a 35% e leitura de disco de 4 a 9 MB/s no vmstat (feed de vulnerabilidades e reconexão dos agentes). A medição "depois" precisa ser feita no mesmo estado (idle estável) e com o mesmo método, senão a comparação engana. O %CPU da tabela "TOP MEMORIA" do script vem do ps (média desde o início do processo); cite o do top e do vmstat.

Observação sobre os arquivos: o texto da coleta das 15:48 UTC (sem swap) NÃO foi salvo em arquivo; ela existe apenas nos prints 02 e 03. Os arquivos em dados/ são: antes_com_swap_16h04.txt (coleta de 16:04:07 UTC, já com swap) e depois.txt (17:07:17 UTC, gerado e salvo na instância por SSH).

### Depois (com Zabbix e HTTPS), 29/10/2026 17:07:17 UTC, uptime 2h25

Condições: Wazuh em repouso (load 0,08 / 0,12 / 0,22; top com 97,7% idle), 3 agentes do Wazuh Active, Zabbix com 1 host (ele mesmo), Zabbix server e agent2 ativos, nginx na 80/443, swap de 2 GB existente. Fonte: dados/depois.txt (script de coleta com as mesmas seções da coleta "antes").

| Métrica | Antes, sem swap (15:48 UTC) | Antes, com swap (16:04 UTC) | Depois (17:07 UTC) |
|---|---|---|---|
| vCPU | 2 | 2 | 2 |
| CPU instantânea (top): us / sy / idle / wa | 1,8 / 0,6 / 97,6 / 0,0 % | 2,1 / 0,6 / 97,1 / 0,0 % | 1,3 / 0,6 / 97,7 / 0,2 % |
| CPU média no vmstat (11 amostras de 5 s): us / sy / idle / wa | não salvo | 1,9 / 1,0 / 97,2 / 0,0 % | 1,6 / 1,0 / 97,1 / 0,2 % |
| Load average 1 / 5 / 15 min | 0,01 / 0,49 / 0,92 | 0,04 / 0,06 / 0,35 | 0,08 / 0,12 / 0,22 |
| RAM usada (MB, de 3831) | 2711 | 2687 | 3000 |
| RAM disponível (MB) | 1120 | 1143 | 830 |
| Swap usada (MB, de 2047) | 0 (sem swap) | 0 | 935 |
| Disco / (usado de 116G) | 19G (17%) | 22G (19%) | 22G (19%) |
| RSS do wazuh-indexer (java) | 1.484.004 KB (1449 MB) | 1.484.704 KB (1450 MB) | 1.276.612 KB (1247 MB) |

Memória do stack do Zabbix (RSS somado por nome de processo, em MB, de depois.txt): mysqld 485, zabbix_server 514, php-fpm 305, nginx 27, zabbix_agent2 22. Cuidado: o RSS soma memória compartilhada várias vezes (o zabbix_server tem dezenas de processos e o php-fpm vários workers), então esses valores são um teto, não um consumo exato.

Leitura (o que os números mostram; a interpretação é minha):
- CPU: sem diferença relevante em repouso. Ficou ~97% ociosa nos três momentos. Isso vale só para a carga atual do Zabbix (1 host, ~2,4 novos valores por segundo, segundo a tela System information). Não foi medida carga com os hosts dos colegas.
- RAM: é o ponto de atenção. Somando RAM usada e swap usada (aproximação do total de memória anônima em uso), o servidor passou de ~2687 MB para ~3935 MB, ou seja, cerca de +1,2 GB com o Zabbix, MySQL, PHP-FPM e nginx. Sobraram 830 MB disponíveis e 935 MB foram para o swap. O indexer do Wazuh encolheu de ~1450 para ~1247 MB de RSS, provavelmente porque o kernel moveu páginas dele para o swap (hipótese, não verificada).
- Swap em atividade: nas 11 amostras do vmstat após a primeira, o swap-in (si) médio foi 6,5 KB/s e o swap-out (so) foi 0. A primeira amostra do vmstat é média desde o boot e foi descartada. Ou seja, no repouso não há paginação intensa, mas o sistema já depende do swap para caber.
- Disco: sem mudança relevante entre antes (com swap) e depois, na precisão do df. Sobram 94G.
- Conclusão provisória: CPU e disco são suficientes; a RAM é suficiente para o repouso atual, mas está no limite (830 MB disponíveis, 935 MB em swap, 4 GiB totais, sem folga para crescimento). Quando Eduardo, Gustavo e Sidney acrescentarem hosts, itens e triggers, o uso de MySQL e do zabbix_server vai subir. Recomendação a discutir com o grupo: subir a instância para t3.large (8 GiB) antes da integração, ou ao menos monitorar swap e memória durante os testes de carga do Sidney. Este é um risco para registrar na Q2 e na Q4. Observação: uma carga de teste de CPU ou rajadas do Wazuh (feed de vulnerabilidades) podem piorar o quadro; elas já fizeram o modulesd passar de 60% de CPU antes.

Evidência: prints 14 a 16 (cat de dados/depois.txt).

## 6. Pendências (o que o próximo precisa fazer)

Obrigatórias para fechar a Tarefa 1:
1. Medição "depois": FEITA (seção 5, dados/depois.txt). Prints do terminal já tirados (14 a 16). Falta repetir a medição depois que os colegas aplicarem os hosts, os alertas e os testes de carga, porque o uso de RAM vai subir, e levar a tabela e a conclusão para o texto da Tarefa 1.
2. Redirecionamento HTTP para HTTPS: FEITO (configs/00-acme.conf já atualizado) e testado por curl de fora. Sem print por decisão do Henrique (ver seção 8).
3. Porta 443 restrita no Security Group g3-sc-wazuh: FEITA PARA UM IP. A regra HTTPS 443 de 0.0.0.0/0 foi trocada por 177.9.102.219/32 (Rick), conforme o print 17 (tela de edição). Verificado de dentro desse IP em 29/10/2026: Zabbix 200, Wazuh 302, porta 80 redirecionando. O bloqueio vindo de outro IP NÃO foi provado: uma tentativa a partir de outro servidor (web_extract) deu erro de túnel e timeout, o que é compatível com o bloqueio mas não conclusivo, e o teste em 4G foi dispensado. FALTA incluir os IPs /32 de Eduardo, Gustavo, Sidney e Lucas: hoje eles NÃO conseguem abrir Zabbix nem Wazuh pelo navegador. A porta 80 continua em 0.0.0.0/0 por causa do Let's Encrypt. O IP residencial pode mudar; se mudar, ajustar a regra pelo console da AWS.
4. Usuários nominais no Zabbix: dispensados por decisão do Henrique (desejável, não necessário). Continua pendente confirmar que a senha do Admin foi trocada (não verificado). Print da lista de usuários só se forem criados.
5. Texto da Tarefa 1 e respostas T1 Q1 a Q4: RASCUNHO PRONTO em texto_tarefa1.md, escrito a partir dos dados reais deste pacote. O autor deve revisar, reescrever no próprio estilo e conferir os números contra os prints. Se houver mudanças (IPs liberados na 443, nova medição, aumento da instância), atualizar as seções 6 e 7 do texto.

Recomendadas (hardening):
6. zabbix_agent2 escuta em *:10050 (todas as interfaces; visto no print 06). Restringir a 127.0.0.1 (ListenIP) e confirmar que o Security Group não expõe 10050 nem 10051.
7. snmpd entrou como dependência (escuta só em localhost, 161/udp). Não é necessário; desativar.
8. 12 itens "not supported" no host Zabbix server (Data collection > Hosts > Items, filtro Not supported). Investigar.
9. Renovação do certificado: testar com "sudo certbot renew --dry-run" e criar um deploy hook para recarregar o nginx.
10. Guardar a senha do banco no gerenciador de senhas e apagar ~/zabbix_db_pass.txt ao final.

Integração com os colegas (Eduardo, Gustavo, Sidney, Lucas):
11. Para monitorar web e db, o Security Group do Wazuh precisa permitir 10051/tcp vindo dos SGs deles (agentes ativos), ou os SGs deles precisam permitir 10050/tcp vindo do SG do Wazuh (passivo). Hoje nenhuma das duas está liberada, de propósito.
12. Passar os dados de acesso ao Zabbix por canal restrito. Credenciais NÃO estão neste pacote.

## 7. Cuidados e lições

- Um "umask 077" ficou ativo na sessão SSH e criou /var/www/letsencrypt com modo 700, causando 403 na validação do Let's Encrypt. Corrigido (chmod 755, umask 022). Verifique permissões ao criar arquivos novos na mesma sessão. O zabbix_server.conf deve continuar 640 root:zabbix; não mexer.
- Em comandos sed colados de chats, evite padrões com asterisco (some na colagem); foi usado o comando "c" do sed com número de linha.
- Rollback do corte da 443: sudo cp -p ~/evidencias/opensearch_dashboards.yml.bak /etc/wazuh-dashboard/opensearch_dashboards.yml && sudo systemctl stop nginx && sudo systemctl restart wazuh-dashboard
- Não rodar "apt upgrade" sem janela combinada (há ~49 pacotes pendentes; reiniciar serviços pode derrubar o Wazuh e invalidar medições).
- A porta 80 aberta ao mundo é necessária só para o Let's Encrypt.
- Depois da restrição da 443, só o IP do Henrique abre as interfaces. Quem precisar acessar deve enviar o IP público (curl -s4 https://api.ipify.org) e o Security Group deve ganhar uma regra HTTPS 443 /32 com a descrição do nome.

## 8. Prints selecionados (pasta prints/)

Só entraram os prints que servem ao relatório da Tarefa 1. A conferência foi feita comparando o texto dos prints (OCR local) com os dados do terminal; a leitura direta por visão não foi possível, então revise a aparência antes de entregar.

| Arquivo | O que comprova | Ajuste sugerido |
|---|---|---|
| 01_ambiente_ec2_instancia | Instância g3-wazuh-server, i-0363e594868beaee8, t3.medium, EIP g3-wazuh-eip, 10.0.4.20 | O ID da conta AWS aparece no topo |
| 02_antes_recursos_cpu_ram_disco | Medição inicial (15:48:44 UTC): SO, CPU, RAM, disco, load, top | Baseline oficial |
| 03_antes_servicos_portas_versoes_agentes | Portas (443 no dashboard), serviços, versões 4.9.2, heap, 3 agentes Active, vmstat, FIM 15:49:42 UTC | |
| 04_swap_2gb_persistente | Swap 2G, fstab, swappiness 10 (16:13:54 UTC) | |
| 05_versoes_instaladas | Zabbix 7.0.32, MySQL 8.4.11, nginx 1.28.3, PHP 8.5.4, Wazuh 4.9.2-1, Ubuntu 26.04.1 (16:14:11 UTC) | |
| 06_conflito_443_wazuh_e_nginx_na_80 | Estado ANTES do corte: 443 ocupada pelo dashboard (node), nginx na 80, MySQL em 127.0.0.1, agent2 em *:10050, 5 serviços active (16:14:22 UTC) | Serve à Q2 e Q3 |
| 07_cloudflare_dns_zabbix_e_monitoramento | Registros A zabbix e monitoramento, 174.129.199.16, DNS only | E-mail da conta borrado |
| 08_security_group_g3-sc-wazuh | 10 regras de entrada, incluindo 80 e 443 em 0.0.0.0/0 | Estado ANTES de restringir a 443 |
| 09_zabbix_acesso_https | Zabbix 7.0 em https://zabbix.maisplace.net.br/setup.php | Cadeado pouco visível na barra; refazer com certificado aberto |
| 10_wazuh_acesso_https_agentes_ativos | Wazuh em https://monitoramento.maisplace.net.br: Agents Active (2), Disconnected (0) | Barra de favoritos mostra outros projetos; recortar |
| 11_zabbix_system_information | Server running, 7.0.32, hosts, templates, itens, triggers | |
| 12_zabbix_hosts_zabbix_server | Host Zabbix server 127.0.0.1:10050, status Enabled | Conferir se o ZBX está verde (não verificado) |
| 13_zabbix_usuarios_guest_desativado | Admin (Super admin role) e guest (Disabled, Guests, Internal) | Controle de acesso |
| 14_depois_recursos_cpu_ram_swap_disco | `cat depois.txt` (topo): coleta de 17:07:17 UTC, uptime 2h25, RAM usada 3000 MB, disponível 830 MB, swap 935 MB, disco 22G, load 0,08, top 97,7% idle | Medição "depois" |
| 15_depois_portas_443_nginx_5601_8080_loopback | Portas depois do corte: 443 e 80 no nginx, dashboard em 127.0.0.1:5601, frontend Zabbix em 127.0.0.1:8080, MySQL em 127.0.0.1, 10051 e 10050 abertos (a restringir) | Substitui o print de portas pós-corte que faltava |
| 16_depois_servicos_versoes_agentes_vmstat | 9 serviços active, versões Wazuh 4.9.2 e Zabbix 7.0.32, 3 agentes Active, RSS por serviço, vmstat estável, FIM 17:08:15 UTC | |
| 17_sg_443_restrita_tela_de_edicao | Security Group g3-sc-wazuh na tela Edit inbound rules: HTTPS 443 só para 177.9.102.219/32 (Rick), HTTP 80 em 0.0.0.0/0, 22 de 3 IPs, 55000, 1514/1515 | É a tela de edição, não a de regras já salvas. Se possível, trocar por um print das regras salvas |

Prints NÃO tirados por decisão do Henrique: certificado aberto pelo cadeado, teste do redirecionamento HTTP para HTTPS (curl) e acesso negado vindo de outro IP. Os resultados desses testes estão descritos em texto na seção 3 (testes feitos por curl de fora da instância), mas sem imagem. Se o relatório precisar dessas evidências, os comandos para reproduzir são: curl -sI http://zabbix.maisplace.net.br (301 para https), clicar no cadeado do navegador (emissor Let's Encrypt, nomes zabbix e monitoramento) e abrir a URL em 4G, sem Wi-Fi (esperado: timeout).
Prints que ainda faltam: lista de usuários nominais do Zabbix e, se possível, as regras do Security Group já salvas.

## 9. Texto da Tarefa 1

texto_tarefa1.md: rascunho completo da Tarefa 1 (verificação de recursos, preparação, instalação, DNS, HTTPS, acesso restrito, comparativo antes e depois) e as respostas às questões Q1 a Q4, com os dados reais deste pacote.

## 9.1. Pasta dados/

antes_com_swap_16h04.txt (coleta de 16:04:07 UTC, com swap) e depois.txt (coleta de 17:07:17 UTC). Não contêm segredos. A coleta das 15:48 UTC só existe nos prints 02 e 03.

## 10. Pasta configs/

Sem segredos: 00-acme.conf, 10-zabbix-tls.conf, 11-wazuh-tls.conf, zabbix-nginx-package-linhas-1-a-3.conf, mysql-zz-zabbix.cnf, wazuh-dashboard-opensearch_dashboards.yml-diff.txt, swap-e-sysctl.txt, zabbix_server.conf-campos-alterados.txt. Senhas, chaves privadas e tokens não estão incluídos.
