### E.HU - 02 (Solicitação de retirada de produto)

> **Como:** Estoquista
**Quero:** Informar que vou retirar um item do almoxarifado
**Para:** Que a Stella registre a solicitação, valide com base no estoque e prepare para confirmação
> 
- **Tecnologias utilizadas**
    1. Comando de voz (ativado por palavra-chave “Stella”)
    2. Tela interativa (para exibir confirmação dos itens)
    
- **Caso de uso proposto**
    1. Estoquista entra no almoxarifado e diz “Stella”
    2. Stella ativa o modo de escuta e aguarda uma frase relacionada a retirada
    3. Estoquista informa os itens (ex: “preciso de 10 seringas de 10ml”)
    4. Stella:
        - Confere o estoque atual
        - Avalia padrões de retirada anteriores (outliers)
        - Aponta inconsistências se houver (ex: estoque insuficiente ou quantidade atípica)
    5. Stella lê ou mostra os itens para revisão e pergunta: “Deseja confirmar essa retirada agora?”
    6. Se o estoquista confirmar, inicia-se a **HU-03 - Validação de retirada**
    7. Se o estoquista não responder ou não confirmar, Stella entra em modo ocioso por 10 minutos
    8. Caso a confirmação não aconteça dentro desse tempo, o pedido é cancelado e uma notificação é enviada ao Sistema de Unidade
    
- **Regras de negócio**
    - RN01 - A Stella deve ser ativada com o comando “Stella” e ignorar conversas não relacionadas à função dela; caso a conversa fuja do propósito, a IA deve encerrar com uma mensagem como “Encerrando sessão, não reconheço essa solicitação como uma retirada.”
    - RN02 - A Stella deve cruzar os itens solicitados com o **estoque real da unidade** e avisar em caso de falta total ou parcial
    - RN03 - A Stella deve comparar os itens solicitados com os **padrões históricos da unidade**, identificando **outliers** (valores muito acima ou abaixo da média)
    - RN04 - Se um valor for considerado fora do padrão (ex: “50 seringas” quando a média é entre 10 e 30), a Stella deve perguntar “Essa quantidade está acima do comum. Deseja continuar mesmo assim?”. Se sim, deve notificar o **Sistema de Unidade**
    - RN05 - A Stella deve manter a solicitação de retirada em aberto por até 10 minutos caso não seja confirmada
    - RN06 - Ao fim do tempo limite sem confirmação, a Stella deve encerrar a solicitação e **notificar o Sistema de Unidade**, informando que a retirada foi cancelada por inatividade
    - RN07 - Apenas uma solicitação de retirada por vez deve estar aberta
    
- **Payload proposto de notificação ao Sistema de Unidade**
    
    ```json
    {
    	 // requerido
    	 "status": "ERRO",
    	 // requerido
       "date":"timestamp",
       // requerido
       "reason":"Solicitação de retirada não confirmada/ ou qualquer outro erro, validar se é melhor tratar como enums",
       // opcional
       "items":[
          {
             "name":"Seringa 10ml",
             "amount":10
          }
       ],
       // requerido
       "chat":[
          {
             "stella":"Você deseja confirmar a retirada de 10 seringas de 10ml?"
          },
          {
             "stockist":"..."
          },
          {
             "stella":"Tempo limite atingido. Cancelando solicitação."
          }
       ]
    }
    
    ```
    

---