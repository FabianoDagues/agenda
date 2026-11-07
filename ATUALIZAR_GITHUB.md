# COMO ATUALIZAR A NOSSA AGENDA (GitHub + Railway)

O ZIP contém o projeto COMPLETO. Os arquivos e pastas `app/`, `Dockerfile`, `requirements.txt`, `README.md` etc. já estão na raiz do ZIP. NÃO envie o ZIP como um único arquivo ao GitHub.

1. Baixe este ZIP e use **Extrair tudo** no Windows.
2. Abra o repositório da agenda na conta correta: https://github.com/FabianoDagues/Agenda
3. Na página inicial do repositório (raiz, onde aparecem `Dockerfile` e `app/`), clique em **Add file > Upload files**.
4. Abra a pasta extraída no Windows, selecione todos os itens **dentro** da pasta (Ctrl+A), inclusive a pasta `app`, e arraste para a área de upload do GitHub. Você deve ver o caminho `app/main.py` e os demais arquivos, sem uma pasta extra por cima.
5. Confirme as substituições de arquivos existentes se o GitHub solicitar. Faça **Commit changes** na branch que o Railway usa (geralmente `main`).
6. No Railway, abra o serviço `agenda` > **Deployments**. Aguarde o NOVO deploy chegar a Success/Online. Verifique que o commit corresponde ao que você acabou de criar no GitHub. Se não iniciar, use a opção de redeploy do commit atualizado ou confira a origem e a branch do serviço.
7. Abra `https://SEU_DOMINIO_PUBLICO/health`: deverá mostrar `"status":"ok"`, `"version":"2.1.0"` e `"database":"postgresql"`. Se `version` não aparecer, o Railway AINDA está rodando código antigo. Se mostrar `sqlite`, não cadastre compromissos reais e revise DATABASE_URL.
8. Abra o domínio público na raiz, acesse a tela de login e teste entrar, salvar compromisso e concluir.

## Variáveis que DEVEM permanecer no serviço `agenda`

- `SECRET_KEY`: chave aleatória privada (já configurada).
- `DATABASE_URL`: referência ao NOVO banco deste projeto, por exemplo `${{Postgres.DATABASE_URL}}`.
- `ADMIN_EMAIL`, `ADMIN_NAME`, `ADMIN_PASSWORD`: conta do primeiro membro.
- `PARTNER_EMAIL`, `PARTNER_NAME`, `PARTNER_PASSWORD`: conta do segundo membro.
- `COOKIE_SECURE=1`, `APP_TIMEZONE=America/Sao_Paulo`.

As senhas devem ter pelo menos 10 caracteres. A troca de `ADMIN_PASSWORD` / `PARTNER_PASSWORD` em Variables NÃO redefine automaticamente a senha de contas já criadas no banco. Nunca envie prints com chaves ou senhas.

## Não faça

- Não exclua o projeto do Railway ou o serviço `Postgres`.
- Não apague o volume do PostgreSQL.
- Não envie somente um ZIP para o repositório, porque o Railway precisa encontrar o `Dockerfile` e a pasta `app`.
- Não altere a aplicação da horta.

## Correção

A versão v2.1 atualiza TODAS as chamadas de `Jinja2Templates.TemplateResponse` para a assinatura `TemplateResponse(request, name, context)` da versão instalada de Starlette, fixa versões compatíveis no `requirements.txt` e adiciona `/health` com `version` para confirmar qual código foi publicado.
