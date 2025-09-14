## 📬 Testando o Webhook (com Segurança)

Este webhook é protegido usando uma assinatura HMAC-SHA256, o padrão de segurança da API do WhatsApp. Para testar, você precisa gerar uma assinatura e enviá-la no cabeçalho `X-Hub-Signature-256`.

1.  **Corpo da Requisição (Body):** Use o JSON que você espera receber.
2.  **Chave Secreta:** Use o valor da sua variável `APP_SECRET` do arquivo `.env`.
3.  **Gere a Assinatura:** Use uma ferramenta online de HMAC-SHA256 para gerar um hash a partir do corpo da requisição e da sua chave secreta.
4.  **Envie a Requisição:** Use uma ferramenta como `curl` ou Postman, incluindo o cabeçalho `X-Hub-Signature-256` com o valor `sha256=<hash_gerado>`.

**Exemplo com `curl`:**
```bash
# Lembre-se de substituir <hash_gerado> pela assinatura que você criou.
curl -X POST http://localhost:5000/ \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=<hash_gerado>" \
  -d '{
    "field": "messages",
    "value": {
      "messages": [
        {"id": "msg1", "from": "5511999999999", "text": {"body": "Olá!"}}
      ]
    }
  }'