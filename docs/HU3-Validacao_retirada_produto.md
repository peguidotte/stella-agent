### E.HU - 03 (Validação para retirada de produto)

> **Como:** Estoquista
> 
> 
> **Quero:** Confirmar a retirada de um ou mais itens
> 
> **Para:** Que a Stella valide minha identidade e registre a retirada no sistema da unidade
> 
- **Tecnologias utilizadas**
    1. Reconhecimento facial (Face ID)
    2. PIN numérico (fallback)
    3. Tela interativa (feedback visual da validação)
    
- **Caso de uso proposto**
    1. Após uma solicitação de retirada (HU-02), a Stella pergunta: “Deseja confirmar essa retirada agora?”
    2. Estoquista responde afirmativamente
    3. Stella inicia o processo de validação por Face ID
    4. O estoquista posiciona o rosto diante do sensor
    5. Stella tenta validar a identidade:
        - Se der certo, registra retirada e encerra processo
        - Se der errado, repete até 3 tentativas
    6. Após 2 falhas, Stella diz: “Última tentativa de reconhecimento facial. Posicione-se corretamente.”
    7. Se a terceira tentativa falhar, Stella oferece alternativa:
        - “Não conseguimos reconhecer seu rosto. Deseja inserir o PIN manual?”
    8. Estoquista insere ou fala o PIN
        - Se o PIN for válido, a Stella registra a retirada
        - Se o PIN for inválido, a Stella notifica o Sistema de Unidade e cancela a validação
    
- **Regras de negócio**
    - RN01 - Validação por Face ID só pode acontecer após uma solicitação de retirada ativa (HU-02)
    - RN02 - São permitidas até 3 tentativas de Face ID consecutivas
    - RN03 - Na terceira tentativa, a Stella deve alertar que é a última tentativa:*“Última tentativa. Garanta que seu rosto esteja visível corretamente.”*
    - RN04 - Em caso de falha nas 3 tentativas, a Stella deve perguntar se o usuário deseja autenticar via PIN
    - RN05 - O PIN digitado deve corresponder ao PIN da unidade vinculado ao usuário autenticado
    - RN06 - Se o PIN estiver correto, a retirada é registrada normalmente
    - RN07 - Se o PIN estiver incorreto, a Stella cancela a retirada e envia notificação de erro ao Sistema de Unidade
    - RN08 - Após qualquer erro (Face ID ou PIN), a retirada deve ser encerrada por segurança e o **Sistema de Unidade** deve ser notificado
    - RN09 - Em caso de sucesso, a Stella deve avisar o estoquista e notificar o **Sistema de Unidade**
    
- **Payloads propostos de notificação ao Sistema de Unidade**
    
    ```json
    {
    	  // requerido
        "status": "ERRO ou SUCESSO",
        // requerido
        "date": "timestamp",
        // apenas enviado se status = SUCESSO
        "user": {
            "idStockist": null,
            "name": null
        },
        // apenas enviado se status = ERRO
        "reason": "Falha na validação facial + PIN incorreto",
        // requerido (importante pra fallback, caso ocorra um erro na stella e o estoquista retire o produto do estoque ele notifica o supervisor de estoque, que consegue manualmente aprovar ou desaprovar a mudança no estoque)
        "items": [
            {
                "name": "Seringa 10ml",
                "amount": 10
            }
        ],
        // requerido
        "chat": [
            {
                "stella": "Você deseja confirmar a retirada de 10 seringas de 10ml?"
            },
            {
                "stockist": "Sim"
            },
            {
                "stella": "Tentando validar sua identidade..."
            },
            {
                "stella": "Falha no reconhecimento. Tentando novamente."
            },
            {
                "stella": "Última tentativa. Posicione-se corretamente."
            },
            {
                "stella": "Não foi possível reconhecer seu rosto. Deseja inserir o PIN?"
            },
            {
                "stockist": "Sim"
            },
            {
                "stella": "PIN inválido. Cancelando retirada e notificando o Sistema de Unidade."
            }
        ]
    }
    
    ```