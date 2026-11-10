# Tarefa 1 - Instalação e configuração do Zabbix (rascunho)

Grupo G3 - Roteiro 4 (Operação e gerenciamento - Zabbix). Responsável: Henrique.
Ambiente: instância g3-wazuh-server (AWS, t3.medium, 2 vCPU, 4 GiB), Ubuntu 26.04.1 LTS. Execução em 29/10/2026.

Observação para o autor: este texto foi escrito a partir dos dados reais coletados na execução (ver HANDOFF.md, dados/ e prints/). Revise, ajuste ao seu estilo e confira cada número contra os prints antes de entregar. Onde algo não foi verificado, o texto diz isso.

## 1. Verificação dos recursos antes da instalação

Antes de instalar qualquer componente, foram coletados CPU, memória, disco, serviços e portas da instância com o Wazuh em funcionamento (prints 01 a 03). Em 29/10/2026 às 15:48 UTC, com 1h06 de uptime e três agentes do Wazuh ativos:

- CPU: 2 vCPU (Intel Xeon Platinum 8259CL). Em repouso, 97,6% ociosa; load average 0,01 / 0,49 / 0,92.
- Memória: 3831 MB no total, 2711 MB usados e 1120 MB disponíveis. Não havia swap.
- Disco: 116 GB no volume raiz, 19 GB usados (17%).
- Maior consumo de memória: o indexer do Wazuh (processo Java), com cerca de 1,45 GB residentes e heap configurado em 1024 MB.
- Portas: 443 ocupada pelo dashboard do Wazuh (aberta em todas as interfaces), 1514, 1515 e 55000 do Wazuh, 22 do SSH, 9200 e 9300 do indexer apenas em loopback. Não havia nginx, Apache nem MySQL instalados.

Durante a preparação, o Wazuh apresentou rajadas de uso: logo após o boot, o processo wazuh-modulesd chegou a 81,8% de CPU, e o vmstat mostrou 19 a 35% de espera de I/O e leitura de disco de 4 a 9 MB/s (atividade de feed de vulnerabilidades e reconexão dos agentes). Por isso a medição de referência foi feita com a plataforma em repouso, e a mesma condição foi exigida na medição posterior.

Avaliação: CPU e disco eram suficientes. A memória disponível (cerca de 1,1 GB) era o ponto crítico, porque o Zabbix com banco de dados e interface Web precisaria de memória adicional. Como a instância não tinha swap, foi criado um swap de 2 GB (persistente em /etc/fstab, swappiness 10) antes da instalação, como proteção contra encerramento de processos por falta de memória (print 04). A medição de referência foi feita antes dessa mudança.

## 2. Preparação do ambiente

- Sistema operacional: Ubuntu 26.04.1 LTS (kernel 7.0.0-1014-aws).
- Versão do Zabbix: 7.0.32 (LTS), com o repositório oficial do Zabbix para Ubuntu 26.04 (pacote zabbix-release 7.0-5). A existência de pacotes para essa versão do Ubuntu foi verificada com o apt antes da instalação.
- Compatibilidade: foi feita uma simulação da instalação (apt install -s) antes de instalar. Ela mostrou que nenhum pacote do Wazuh seria alterado ou removido e que o Apache não seria instalado. Entraram como dependências o PHP 8.5.4 (php-fpm) e o snmpd.
- Componentes escolhidos: zabbix-server-mysql, zabbix-frontend-php, zabbix-nginx-conf, zabbix-sql-scripts, zabbix-agent2, MySQL 8.4.11 e nginx 1.28.3.

## 3. Instalação do Zabbix

- Banco de dados: MySQL 8.4.11, escutando apenas em 127.0.0.1. Para não competir por memória com o indexer do Wazuh, foram definidos innodb_buffer_pool_size de 256 MB, performance_schema desligado e log binário desligado. Foi criado o banco zabbix (utf8mb4, collation utf8mb4_bin) e um usuário zabbix restrito a localhost, com senha aleatória. O esquema do Zabbix foi importado (203 tabelas, 45 segundos).
- Servidor Zabbix: configurado com as credenciais do banco; escuta na porta 10051.
- Interface Web: servida pelo nginx com PHP-FPM, inicialmente apenas em 127.0.0.1:8080. O assistente de instalação web foi concluído com todos os pré-requisitos aprovados (PHP 8.5.4 contra o mínimo exigido de 8.0.0) e o fuso horário America/Sao_Paulo.
- Conflito de portas com o Wazuh: o dashboard do Wazuh ocupava a 443. A solução está na seção 5.
- Agente: o zabbix-agent2 foi instalado no próprio servidor, e o host "Zabbix server" aparece cadastrado (print 12).

Versões instaladas (print 05): Zabbix 7.0.32, MySQL 8.4.11, nginx 1.28.3, PHP 8.5.4, Wazuh 4.9.2-1 (manager, indexer, dashboard).

## 4. Configuração do DNS na Cloudflare

Foi criado no domínio maisplace.net.br o registro A "zabbix" apontando para 174.129.199.16, o Elastic IP da instância de monitoramento, no modo DNS only (print 07). O registro "monitoramento", do Wazuh, já existia com o mesmo IP e o mesmo modo.

Escolha do modo DNS only: o roteiro não define proxy ou DNS only. O tráfego dos agentes do Wazuh (portas 1514 e 1515) não passa pelo proxy da Cloudflare, e o nome "monitoramento" já era DNS only. Como esse nome já expõe o mesmo IP, passar o "zabbix" pelo proxy não esconderia o endereço. A consequência é que o certificado precisa ser publicamente confiável (não pode ser o certificado de origem da Cloudflare) e que o controle de acesso fica no Security Group e no login das plataformas, não no Cloudflare Access.

## 5. Acesso Web com HTTPS e coexistência com o Wazuh

- Certificado: Let's Encrypt, emitido com o certbot pelo método webroot (HTTP-01), um único certificado cobrindo zabbix.maisplace.net.br e monitoramento.maisplace.net.br (SAN). Validade de 29/10/2026 a 27/01/2027, com renovação automática pelo certbot.timer. Para a validação, a porta 80 foi liberada no Security Group.
- Reverse proxy: o nginx passou a ser o único serviço na porta 443. O dashboard do Wazuh foi movido para 127.0.0.1:5601 (apenas duas linhas alteradas no opensearch_dashboards.yml, com backup) e a interface do Zabbix permaneceu em 127.0.0.1:8080. O nginx tem dois blocos server na 443, um por nome (zabbix e monitoramento), cada um repassando para o respectivo serviço local. O Wazuh ficou indisponível por cerca de 1 a 2 minutos durante a troca.
- HTTP: a porta 80 redireciona para HTTPS (301), mantendo o caminho /.well-known/acme-challenge/ acessível para a renovação do certificado.
- Validação a partir de fora da instância: https://zabbix.maisplace.net.br respondeu 200 e https://monitoramento.maisplace.net.br respondeu 302 (redirecionamento para a tela de login), ambos com certificado verificado. Os dois agentes do Wazuh (web-server e db-server) continuaram ativos após a troca de porta (prints 09 e 10).

## 6. Acesso restrito

- Security Group g3-sc-wazuh: a porta 443 deixou de estar aberta para qualquer origem e foi restringida a um endereço /32 (print 17). Isso segue o padrão já usado pelo grupo nos roteiros anteriores, que restringe o SSH (22) e a API do Wazuh (55000) a endereços /32. As portas 1514 e 1515 continuam liberadas apenas aos Security Groups do servidor web e do banco. A porta 80 permanece aberta, apenas para o Let's Encrypt.
- Zabbix: o usuário guest está desativado (grupos Disabled, Guests e Internal) e há apenas o usuário Admin com o papel Super admin (print 13). Não foram criados usuários nominais para cada integrante; isso é desejável, mas não era necessário para esta tarefa e não foi feito.
- Limitação: hoje apenas um endereço IP tem acesso à porta 443. Os endereços dos demais integrantes ainda precisam ser incluídos. Não foi comprovado, por teste a partir de outro endereço, que o acesso é bloqueado; o resultado do Security Group foi conferido na configuração e o acesso foi validado a partir do endereço liberado.

## 7. Validação e consumo de recursos depois da instalação

Medição de 29/10/2026 às 17:07 UTC, uptime de 2h25, com o Wazuh em repouso (load average 0,08 / 0,12 / 0,22), os três agentes do Wazuh ativos e o Zabbix monitorando apenas o próprio servidor (prints 14 a 16). Os serviços wazuh-manager, wazuh-indexer, wazuh-dashboard, filebeat, zabbix-server, zabbix-agent2, mysql, nginx e php8.5-fpm estavam todos ativos, e a interface do Zabbix mostrava o servidor em execução na versão 7.0.32 (print 11).

| Métrica | Antes, sem swap (15:48 UTC) | Antes, com swap (16:04 UTC) | Depois (17:07 UTC) |
|---|---|---|---|
| vCPU | 2 | 2 | 2 |
| CPU instantânea (top): us / sy / idle / wa | 1,8 / 0,6 / 97,6 / 0,0 % | 2,1 / 0,6 / 97,1 / 0,0 % | 1,3 / 0,6 / 97,7 / 0,2 % |
| Load average 1 / 5 / 15 min | 0,01 / 0,49 / 0,92 | 0,04 / 0,06 / 0,35 | 0,08 / 0,12 / 0,22 |
| RAM usada (MB, de 3831) | 2711 | 2687 | 3000 |
| RAM disponível (MB) | 1120 | 1143 | 830 |
| Swap usada (MB, de 2047) | sem swap | 0 | 935 |
| Disco usado (de 116 GB) | 19 GB (17%) | 22 GB (19%) | 22 GB (19%) |

Análise:
- CPU: sem diferença relevante em repouso (cerca de 97% ociosa nos três momentos). O resultado vale para a carga atual do Zabbix, com um único host monitorado, e não foi medido com os servidores dos demais integrantes.
- Disco: o aumento de 19 para 22 GB já aparece na coleta feita antes da instalação do Zabbix (a que tem swap) e coincide com a criação do arquivo de swap de 2 GB; entre essa coleta e a posterior o valor não mudou na precisão do comando df. Restam 94 GB livres, o que é suficiente.
- Memória: é o ponto crítico. Somando memória usada e swap usado, o servidor passou de cerca de 2687 MB para 3935 MB, um aumento aproximado de 1,2 GB atribuível ao Zabbix, MySQL, PHP-FPM e nginx. A memória disponível caiu de 1143 para 830 MB e 935 MB passaram para o swap. Nas amostras de vmstat após a primeira, o swap-in médio foi de 6,5 KB/s e o swap-out foi zero, ou seja, em repouso não há paginação intensa, mas o sistema já depende do swap.
- Conclusão: os recursos são suficientes para a execução simultânea das duas plataformas na carga atual, mas a memória está no limite e sem folga para o crescimento esperado quando os servidores web e de banco, os alertas e os testes de carga forem adicionados. Recomenda-se aumentar a instância (por exemplo, t3.large, com 8 GiB) antes da integração, ou ao menos acompanhar o uso de memória e swap durante os testes.

## 8. Respostas às questões

### Questão 1. Quais são os principais componentes necessários para o funcionamento do Zabbix e qual a função de cada um?

- Zabbix Server: é o núcleo da plataforma. Recebe e processa os dados coletados, avalia as expressões das triggers, gera eventos e problemas, dispara as ações (como notificações) e grava tudo no banco. Nesta instalação, ele escuta na porta 10051.
- Banco de dados: armazena a configuração (hosts, itens, templates, triggers, usuários) e o histórico e as tendências das métricas. Nesta instalação é um MySQL 8.4.11 local, com 203 tabelas. É o componente mais sensível em desempenho e espaço em disco.
- Interface Web (frontend): aplicação PHP usada para configurar e visualizar o ambiente (dashboards, hosts, gráficos, problemas, usuários). Acessa o banco diretamente e conversa com o servidor. Aqui é servida pelo nginx com PHP-FPM.
- Agente (Zabbix Agent/Agent 2): roda nos servidores monitorados e coleta métricas locais (CPU, memória, disco, rede, processos e serviços), enviando-as ao servidor. Funciona no modo passivo (o servidor consulta, porta 10050) ou ativo (o agente envia ao servidor). Nesta instalação o agent2 monitora o próprio servidor.
- Zabbix Proxy (opcional): coleta dados em nome do servidor em redes remotas ou grandes, reduzindo a carga e a exposição do servidor. Não foi usado.
- Conceitos de configuração que dependem desses componentes: host (o que é monitorado), item (a métrica coletada), trigger (a condição que gera um problema a partir de itens) e template (conjunto reutilizável de itens, triggers e gráficos aplicável a vários hosts). A instalação traz 356 templates e, ao final, havia 153 itens e 83 triggers associados ao host do servidor.

### Questão 2. Quais cuidados devem ser considerados ao instalar duas plataformas de monitoramento na mesma instância?

- Dimensionamento de memória: é o recurso mais disputado. O indexer do Wazuh (Java) reserva memória própria e o MySQL e o servidor do Zabbix também consomem. Aqui, a memória disponível era de cerca de 1,1 GB antes e de 830 MB depois, e foi necessário criar swap e limitar o MySQL (buffer de 256 MB, sem performance_schema nem log binário).
- CPU e I/O de disco: o Wazuh tem rajadas (atualização de feed de vulnerabilidades, reconexão de agentes) que chegaram a 82% de CPU e 35% de espera de I/O. A medição de consumo deve ser feita com as duas plataformas em condições comparáveis, e testes de carga devem considerar isso.
- Conflito de portas: o dashboard do Wazuh ocupava a 443. A solução foi mover o dashboard para a loopback (5601) e usar um proxy reverso na 443. Convém mapear as portas antes (ss -tlnp) e manter os serviços internos em 127.0.0.1.
- Compatibilidade e isolamento: verificar versão do sistema, pacotes e dependências antes de instalar, para não alterar componentes do Wazuh (feito com simulação do apt). Evitar atualizações em massa na instância (apt upgrade), porque reiniciar serviços pode derrubar o Wazuh e invalidar medições.
- Janela e ordem das mudanças: a mudança de porta do dashboard deixou o Wazuh indisponível por 1 a 2 minutos; mudanças como essa devem ter janela combinada e plano de reversão (houve backup da configuração).
- Segurança e acesso: manter uma única porta pública (443), fechar as portas internas dos serviços (3306, 5601, 8080, 9200) e restringir origens no Security Group. O agente do Zabbix e o snmpd não devem ficar expostos sem necessidade.
- Armazenamento: reservar disco para o histórico do Zabbix e para os índices do Wazuh, e definir retenção e housekeeping.
- Operação: separar usuários, senhas e backups de cada plataforma, e monitorar a própria instância (inclusive swap e memória) para detectar o problema antes de ele afetar as duas plataformas.

### Questão 3. Como é possível disponibilizar Zabbix e Wazuh por subdomínios diferentes, utilizando o mesmo endereço IP e a porta HTTPS/443?

Por meio de hospedagem virtual baseada em nome (virtual hosts) em um servidor web ou reverse proxy que escute a porta 443:

1. DNS: cada subdomínio recebe um registro A apontando para o mesmo IP. Aqui, zabbix.maisplace.net.br e monitoramento.maisplace.net.br apontam para 174.129.199.16.
2. Identificação do site: o cliente informa o nome desejado de duas formas. Na negociação TLS, envia o nome na extensão SNI (Server Name Indication), o que permite ao servidor escolher o certificado correto antes de qualquer dado HTTP. Depois, na requisição HTTP, envia o cabeçalho Host.
3. Roteamento: o nginx tem um bloco server por nome, selecionado por server_name. O bloco do zabbix repassa para a interface em 127.0.0.1:8080, e o do monitoramento repassa para o dashboard do Wazuh em 127.0.0.1:5601 (por HTTPS interno, com suporte a WebSocket).
4. Certificado: precisa cobrir os dois nomes. Foi usado um único certificado Let's Encrypt com os dois nomes (SAN). Alternativas são um certificado por nome ou um certificado curinga.
5. Serviços internos: o que realmente atende cada aplicação fica em portas locais diferentes (8080 e 5601), sem exposição externa. Só a 443 (e a 80, para redirecionamento e renovação do certificado) fica pública.

Observação: se o cliente não enviar SNI ou pedir um nome desconhecido, o nginx usa o primeiro bloco da 443 como padrão (aqui, o do Zabbix). É um detalhe a conhecer, não um problema para os nomes configurados. Sem esse compartilhamento por nome, seria preciso expor as plataformas em portas diferentes (por exemplo, 8443) ou em caminhos diferentes do mesmo site (path-based).

### Questão 4. Quais riscos operacionais e de segurança podem surgir ao concentrar duas plataformas críticas em uma única instância?

Riscos operacionais:
- Ponto único de falha: uma queda da instância, do disco ou do nginx derruba ao mesmo tempo o monitoramento de desempenho e o de segurança, justamente quando mais são necessários.
- Disputa por recursos: as plataformas competem por CPU, memória e I/O. Na prática, a memória disponível caiu de 1,1 GB para 830 MB e 935 MB foram para swap com apenas um host no Zabbix, e as rajadas do Wazuh já chegaram a 82% de CPU. Crescimento de hosts, itens ou alertas pode causar lentidão, perda de coleta ou encerramento de processos por falta de memória.
- Manutenção acoplada: atualizações, reinicializações e mudanças em uma plataforma afetam a outra (por exemplo, a troca de porta do dashboard deixou o Wazuh fora do ar por alguns minutos). Falhas de atualização têm impacto maior.
- Quem monitora o monitor: se a instância falha, nenhuma das duas plataformas avisa; é preciso uma verificação externa.
- Backup e recuperação: dois bancos e dois conjuntos de dados em um só disco aumentam o tempo e a complexidade de restauração.

Riscos de segurança:
- Superfície de ataque e "raio de explosão": comprometer a instância, o nginx ou a conta com acesso a ela expõe os dados das duas plataformas (inventário, métricas, alertas de segurança) e as credenciais de coleta. Aqui, o proxy na 443 é um ponto comum às duas.
- Adulteração de evidências: um invasor com acesso ao servidor pode alterar ou apagar registros e alertas do Wazuh, comprometendo a investigação, e usar o Zabbix para entender o ambiente.
- Exposição indevida: portas e serviços adicionais (agente do Zabbix em todas as interfaces, snmpd, 10051) ampliam a superfície se o Security Group for permissivo. Antes da restrição, a 443 estava aberta para qualquer origem.
- Certificado e chaves compartilhados: um único certificado para os dois nomes significa que o vazamento da chave afeta as duas interfaces.
- Credenciais: o servidor guarda senhas de banco e de aplicação em arquivos locais; a segregação de funções entre as duas plataformas fica mais difícil.

Mitigações possíveis: separar as plataformas em instâncias distintas quando o crescimento exigir; restringir o acesso por IP no Security Group e exigir autenticação nominal e MFA; manter backups e snapshots testados; monitorar a instância de fora (inclusive memória e swap); enviar os logs do Wazuh para outro local; limitar os serviços a 127.0.0.1; e manter janelas de manutenção combinadas e plano de reversão.

## 9. Evidências

Os prints citados estão na pasta prints/ do pacote, numerados de 01 a 17. As configurações usadas (nginx, MySQL, swap, alteração do dashboard do Wazuh) estão em configs/, e as coletas de consumo de recursos estão em dados/. Prints não tirados nesta execução (certificado aberto no navegador, teste do redirecionamento e acesso negado vindo de outro endereço) estão listados no HANDOFF.md, com a forma de reproduzir.
