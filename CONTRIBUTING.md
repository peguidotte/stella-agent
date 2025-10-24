# Contribuindo para Stella Agent

Obrigado por considerar contribuir com o Stella Agent! 🎉

## 📋 Código de Conduta

Este projeto segue um Código de Conduta. Ao participar, você concorda em manter um ambiente respeitoso e acolhedor.

## 🚀 Como Contribuir

### Reportando Bugs

Antes de criar um issue, verifique se o bug já não foi reportado. Se não encontrou, crie um novo issue incluindo:

- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs. observado
- Versão do Python e dependências
- Logs relevantes (se disponível)

### Sugerindo Melhorias

Issues para sugestões são bem-vindos! Inclua:

- Descrição clara da funcionalidade
- Justificativa (por que seria útil)
- Possíveis casos de uso

### Pull Requests

1. **Fork** o repositório
2. **Clone** seu fork: `git clone https://github.com/seu-usuario/stella-agent.git`
3. **Crie uma branch** para sua feature: `git checkout -b feature/minha-feature`
4. **Configure o ambiente de desenvolvimento**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # ou .\venv\Scripts\activate no Windows
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # se disponível
   ```

5. **Faça suas alterações** seguindo os padrões do projeto
6. **Execute os testes** (quando disponíveis):
   ```bash
   pytest
   ```

7. **Commit suas mudanças**:
   ```bash
   git add .
   git commit -m "feat: adiciona nova funcionalidade X"
   ```

8. **Push para seu fork**:
   ```bash
   git push origin feature/minha-feature
   ```

9. **Abra um Pull Request** no repositório original

### Padrões de Commit

Usamos Conventional Commits:

- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Mudanças na documentação
- `style:` - Formatação, ponto e vírgula, etc
- `refactor:` - Refatoração de código
- `test:` - Adição ou correção de testes
- `chore:` - Atualizações de build, etc

Exemplo: `feat: adiciona validação de PIN com timeout`

## 💻 Padrões de Código

### Python

- Use Python 3.11+
- Siga PEP 8
- Use type hints quando possível
- Docstrings para funções públicas (estilo Google)
- Máximo de 100 caracteres por linha

Exemplo:

```python
def process_speech(text: str, session_id: str) -> SpeechResponse:
    """
    Processa entrada de voz usando IA.
    
    Args:
        text: Texto transcrito da fala
        session_id: Identificador da sessão
        
    Returns:
        Resposta processada pela IA
        
    Raises:
        ValueError: Se o texto estiver vazio
    """
    if not text:
        raise ValueError("Texto não pode estar vazio")
    
    # ... implementação
```

### Estrutura de Arquivos

- Mantenha módulos pequenos e focados
- Um arquivo por classe/serviço principal
- Use `__init__.py` para expor APIs públicas
- Organize por domínio/funcionalidade

### Testes

- Escreva testes para novas funcionalidades
- Use pytest
- Nomenclatura: `test_<funcao>_<cenario>.py`
- Mire em cobertura > 80%

## 🔍 Processo de Review

1. Todos os PRs passam por code review
2. CI deve passar (quando configurado)
3. Ao menos 1 aprovação necessária
4. Mudanças solicitadas devem ser endereçadas

## 📚 Recursos

- [Documentação da API](./README.md)
- [Guia de Instalação](./INSTALLATION_GUIDE.md)
- [Respostas Assíncronas](./ASYNC_RESPONSES.md)

## 💬 Dúvidas?

- Abra uma issue com a tag `question`
- Entre em contato com a equipe Stellar

Obrigado por contribuir! 🌟
