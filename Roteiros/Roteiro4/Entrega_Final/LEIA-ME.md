# Roteiro 4: entrega final

`Roteiro4_Relatorio_Final.docx` é o documento de entrega (4 tarefas, 18 respostas, 39 figuras).

## Como regerar o DOCX

O texto fica nos scripts. Para alterar o relatório, edite-os e rode nesta pasta:

```bash
pip install python-docx
python build.py Roteiro4_Relatorio_Final.docx
```

- `build.py`: capa, Tarefas 2 a 4 e conclusões.
- `t1_section.py`: Tarefa 1, a partir de `../Henrique_Tarefa1_handoff/`.
- `t3_testes.py`: resultados dos testes de alerta.
- `evidencias_sidney/` e `evidencias_lucas/`: figuras usadas no documento.

## Estado do ambiente em 10/11/2026

| Item | Situação |
|---|---|
| Hosts no Zabbix | Zabbix server, db-01, jump-01 e web-01, todos disponíveis |
| web-01 | Template Linux by Zabbix agent active, com itens próprios do Apache |
| Dashboard | "G3 - Visao geral (Roteiro 4)" |
| Triggers do grupo | Tag `grupo = G3-roteiro4` |
| E-mail | Tipo de mídia Email e ação "Report problems to Zabbix administrators" ativos |

## Pontos de atenção

- O db-01 tem 1 GB de RAM, sem swap, e já travou várias vezes. Se o site mostrar erro de banco, reinicie a instância.
- O acesso às interfaces depende do seu IP nas regras 443 e 22 do Security Group `g3-sc-wazuh`.
- Senhas e chaves não devem ser adicionadas a este repositório.
