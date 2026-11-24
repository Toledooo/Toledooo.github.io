# Portfólio automatizado

Site estático bilíngue (PT-BR e EN) gerado em Python a partir dos meus repositórios do GitHub e publicado no GitHub Pages: <https://toledooo.github.io>

## Como funciona

1. O workflow roda em cada push na `main`, toda segunda-feira e manualmente (aba **Actions → Publicar portfólio → Run workflow**).
2. `python -m generator` lê a API pública do GitHub e escolhe os repositórios **públicos** com o topic `portfolio`, sem forks nem arquivados. O topic `no-portfolio` exclui um repositório.
3. Os textos vêm de `profile.yml` (perfil) e `projects.yml` (projetos), nos dois idiomas. Sem entrada em `projects.yml`, o site usa a descrição do GitHub e avisa no log do workflow.
4. Se qualquer etapa falhar (API fora do ar, teste quebrado), o deploy não roda e o site publicado continua como estava.

## Adicionar um projeto

1. No repositório do projeto, adicione o topic `portfolio` (engrenagem ao lado de **About**).
2. Opcional: coloque uma imagem em `docs/preview.png` no repositório do projeto (PNG de até 3 MB). Sem ela, o site gera um cartão animado.
3. Opcional: descreva o projeto nos dois idiomas em `projects.yml` (há um exemplo comentado lá).
4. Rode o workflow, ou espere a próxima segunda-feira.

## Configuração

| Onde | Nome | Para quê |
| --- | --- | --- |
| Settings → Pages | Source: **GitHub Actions** | publicar o site |
| Settings → Secrets and variables → Actions → **Variables** | `CONTACT_URL` | URL do canal de chamados. Vazia, o botão "Abrir chamado" não aparece |

Textos fixos da interface ficam em `strings.yml`. O visual, em `generator/static/style.css`.

## Desenvolvimento local

```bash
pip install -r requirements-dev.txt
python -m pytest                                              # testes
python -m generator --fixture tests/fixtures/repos.json       # site com dados de exemplo, sem rede
python -m generator                                           # site real (GITHUB_TOKEN opcional)
python -m http.server -d dist 8000                            # ver em http://localhost:8000
```

## Observações

- O GitHub desativa workflows agendados em repositórios públicos sem atividade por 60 dias. O push ou o disparo manual reativa.
- Para publicar em um endereço de projeto (`usuario.github.io/nome`), defina `BASE_PATH=/nome` no passo de build.
- O gerador está pronto para uma etapa futura de IA nas descrições, mas hoje não usa nenhuma.

## Próximas etapas (v2)

Clipes animados por projeto (Manim), README do perfil gerado automaticamente, checagem Lighthouse e integração com o canal de chamados.
