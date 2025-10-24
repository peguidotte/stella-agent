# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Added
- LICENSE (MIT License)
- CONTRIBUTING.md com guia de contribuição
- CODE_OF_CONDUCT.md
- CHANGELOG.md para rastreamento de mudanças
- .env.example com template de variáveis de ambiente
- .editorconfig para consistência de código
- SECURITY.md para reporte de vulnerabilidades

### Changed
- Melhorias na documentação do README.md

## [1.0.0] - 2025-01-XX

### Added
- Sistema de autenticação com Face ID e PIN (HU-01)
- Processamento de voz com IA Gemini para solicitações de retirada (HU-02)
- Validação de retirada com reconhecimento facial (HU-03)
- API REST com FastAPI
- Comunicação assíncrona via WebSocket (Pusher)
- Sistema de detecção de outliers em retiradas
- Integração com RabbitMQ para comunicação com Sistema da Unidade
- Configuração flexível via YAML
- Sistema de sessões com timeouts
- Reconhecimento facial com DeepFace
- Processamento de linguagem natural em português

### Documentation
- README.md com diagramas de fluxo
- INSTALLATION_GUIDE.md com guia detalhado de instalação
- ASYNC_RESPONSES.md com documentação de eventos WebSocket
- Histórias de usuário (HU-01, HU-02, HU-03) documentadas

[Unreleased]: https://github.com/peguidotte/stella-agent/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/peguidotte/stella-agent/releases/tag/v1.0.0
