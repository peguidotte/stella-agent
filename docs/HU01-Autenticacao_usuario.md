### E.HU - 01 (Autenticação de usuário)

> **Como:** Estoquista
**Quero:** Estar autenticado
**Para:** Ter permissão de gerenciar o almoxarifado
> 
- **Tecnologias utilizadas**
    1. Reconhecimento facial (Face ID)
    2. Comando de voz
    3. PIN numérico
    
- **Caso de uso proposto**
    1. Iniciar autenticação por comando de voz (“Autenticação”) ou botão
    2. Informar PIN da unidade (via voz ou digitação)
    3. Confirmar PIN após pergunta da Stella
    4. Associar autenticação com Face ID
    5. Inserir ou dizer o nome
    6. Confirmar tudo
    
- **Regras de negócio**
    - RN01 - Cada Sistema de Unidade deve possuir um PIN de 6 dígitos para autenticação com a Stella, esse PIN pode ser alterado a qualquer hora de dentro do sistema.
    - RN02 - A Stella deve confirmar cada ação com o Usuário, ao inserir ou falar um PIN, a Stella deve falar “Você confirma esse PIN?”. Só deve executar uma tentativa pós confirmação, caso não haja, deve reiniciar a tentativa pedindo ao usuário informar novamente um PIN.
    - RN03 -  Caso o PIN seja inválido a Stella deve informar que o PIN é inválido e que o usuário possui mais X tentativas. **O número máximo de tentativas é 3**. “PIN inválido, você possui mais 2 tentativas”
    - RN04 - Caso o usuário esteja na última tentativa de informar o PIN, a Stella deve informar “PIN inválido, você está na última tentativa. Garanta que o PIN inserido é o correto”
    - RN05 - Caso todas as tentativas falharem, a Stella deve avisar o usuário (”Todas as tentativas falharam, enviamos uma notificação ao Sistema de Unidade, bloquearemos a autenticação por 30 minutos, esse bloqueio pode ser cancelado pelo Sistema de Unidade”) e em seguida enviar notificação ao **Sistema de Unidade.**
    - RN06 - O Sistema de Unidade deve ser capaz de desbloquear a autenticação ou bloquear por outros períodos.
    - RN07 - Em caso de PIN informado com sucesso, a Stella deve exigir nome e sobrenome do usuário depois de cadastrar Face ID, deve haver confirmação do nome.
    - RN08 - Em caso de autenticação com sucesso, o **Sistema de Unidade** deve ser capaz de visualizar e gerenciar o usuário autenticado.
    
- **Payloads propostos de notificação ao Sistema de Unidade**
    
    Sucesso:
    
    ```json
    {
    	 // requerido
    	 "status": "SUCESSO",
    	 // requerido
       "idStockist":"uuid (gerado automaticamente)",
       // requerido
       "name":"{nome informado}",
       // requerido
       "data":"timestamp do dia e horário da notificação",
       // requerido
       "chat":[
          {
             "stella":"blablabla"
          },
          {
             "stockist":"blablabla"
          }
       ]
    }
    ```
    
    Erro:
    
    ```json
    {
    	 // requerido
    	 "status": "ERRO",
    	 // requerido
       "date":"timestamp do dia e horário da notificacao",
       // requerido
       "pins":[
          {
             "1":"121911"
          },
          {
             "2":"191921"
          },
          {
             "3":"191922"
          }
       ],
       // requerido
       "message":"Numero de tentativas execedidas, autenticação bloqueada por 30 minutos",
       // requerido
       "chat":[
          {
             "stella":"blablabla"
          },
          {
             "stockist":"blablabla"
          }
       ]
    }
    ```