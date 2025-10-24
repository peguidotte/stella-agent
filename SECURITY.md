# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

A segurança do Stella Agent é levada a sério. Se você descobrir uma vulnerabilidade de segurança, por favor reporte de forma responsável.

### Como Reportar

**NÃO** crie uma issue pública para vulnerabilidades de segurança.

Em vez disso:

1. **Email**: Entre em contato com a equipe através de um email privado (adicione o email apropriado aqui)
2. **Informações a incluir**:
   - Tipo de vulnerabilidade
   - Localização do código afetado (arquivo/linha)
   - Passos para reproduzir
   - Impacto potencial
   - Sugestões de correção (se possível)

### O que Esperar

- **Confirmação**: Responderemos em até 48 horas
- **Atualizações**: Manteremos você informado sobre o progresso
- **Crédito**: Daremos crédito apropriado (se desejar)
- **Timeline**: Correção em até 90 dias (dependendo da gravidade)

### Vulnerabilidades Conhecidas

Atualmente não há vulnerabilidades conhecidas reportadas.

## Melhores Práticas de Segurança

Ao usar o Stella Agent:

### Variáveis de Ambiente

- **NUNCA** commite arquivos `.env` com credenciais reais
- Use `.env.example` como template
- Mantenha suas API keys seguras
- Rotacione credenciais regularmente

### PIN da Unidade

- Altere o PIN padrão (`123456`) imediatamente
- Use PINs fortes (6 dígitos aleatórios)
- Configure via variável de ambiente `STELLA_UNIT_PIN`

### Face ID

- Armazene encodings faciais de forma segura
- Considere criptografia para dados sensíveis
- Implemente backups seguros

### API Keys

- **GEMINI_API_KEY**: Proteja sua chave da API Google
- **PUSHER_***: Mantenha credenciais Pusher privadas
- **CLOUDAMQP_URL**: Proteja URL de conexão AMQP

### Deploy em Produção

- Use HTTPS/TLS para todas as comunicações
- Configure CORS adequadamente (não use `*` em produção)
- Implemente rate limiting
- Use secrets management (AWS Secrets Manager, Azure Key Vault, etc.)
- Habilite logging de auditoria
- Configure firewalls apropriados

## Atualizações de Segurança

Atualizações de segurança serão anunciadas via:

- Issues do GitHub (para vulnerabilidades resolvidas)
- CHANGELOG.md
- Releases do GitHub

## Recursos de Segurança Implementados

- ✅ Autenticação multi-fator (PIN + Face ID)
- ✅ Limite de tentativas de autenticação
- ✅ Lockout após tentativas falhas
- ✅ Timeout de sessão
- ✅ Validação de entrada
- ✅ Logs de auditoria

## Recursos de Segurança Planejados

- [ ] Criptografia de dados em repouso
- [ ] Rate limiting por IP
- [ ] 2FA para administradores
- [ ] Auditoria completa de logs
- [ ] Penetration testing

---

Obrigado por ajudar a manter o Stella Agent seguro! 🔒
