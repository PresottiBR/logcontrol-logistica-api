# LogControl – API de Logística

## Apresentação

O LogControl é um sistema desenvolvido com o objetivo de auxiliar no controle e gerenciamento de processos logísticos.

Este projeto corresponde à API de Logística do sistema e foi desenvolvido dentro de uma proposta de MVP (Minimum Viable Product), utilizando uma arquitetura baseada em API REST.

A API foi criada para atender a necessidades relacionadas ao gerenciamento de endereços de clientes e ao cálculo de rotas. Para isso, além do banco de dados próprio da aplicação, foram utilizadas integrações com serviços externos de consulta de CEP, geocodificação e cálculo de rotas.

A solução foi desenvolvida considerando um cenário B2B, no qual as informações de clientes e endereços podem ser utilizadas como base para operações logísticas.

---

## Objetivo

O principal objetivo da API é disponibilizar recursos para consulta e gerenciamento de endereços, além de fornecer informações de rota entre diferentes localidades.

Entre as principais funcionalidades desenvolvidas estão:

• Consulta de endereço através do CEP;

• Cadastro de endereços vinculados a clientes;

• Consulta de endereços cadastrados;

• Atualização de endereços;

• Exclusão de endereços;

• Validação das informações recebidas pela API;

• Integração com serviços externos;

• Cálculo de distância e duração estimada de uma rota;

• Persistência dos dados utilizando PostgreSQL;

• Documentação dos endpoints através do Swagger.

---

## Tecnologias utilizadas

O projeto foi desenvolvido utilizando as seguintes tecnologias:

**Python 3.13**  
Linguagem utilizada no desenvolvimento da aplicação.

**Flask**  
Framework utilizado para criação da API REST e gerenciamento das rotas.

**Flasgger / Swagger**  
Utilizado para documentação e testes dos endpoints disponibilizados pela API.

**PostgreSQL 16**  
Banco de dados relacional utilizado para persistência das informações.

**Psycopg**  
Biblioteca utilizada para realizar a comunicação entre a aplicação Python e o PostgreSQL.

**Docker**  
Utilizado para criação e execução dos ambientes da aplicação e do banco de dados.

**Docker Compose**  
Utilizado para facilitar a configuração e inicialização dos containers.

---

## Estrutura do projeto

A API está organizada de forma a separar as rotas da aplicação dos serviços responsáveis pelas integrações e comunicação com o banco de dados.

logistica-api/

    routes/
        logistica.py

    services/
        banco.py
        geocodificacao.py
        osrm.py
        viacep.py

    app.py
    requirements.txt
    Dockerfile
    README.md

O arquivo `app.py` é responsável pela inicialização da aplicação Flask e pelo registro das rotas.

O arquivo `routes/logistica.py` concentra os endpoints relacionados às funcionalidades de logística.

A pasta `services` contém os módulos responsáveis pela comunicação com o banco de dados e pelos serviços externos utilizados pela aplicação.

---

## Banco de dados

A aplicação utiliza o PostgreSQL 16 como banco de dados.

A comunicação com o banco é realizada através da biblioteca Psycopg e utiliza variáveis de ambiente para configuração da conexão.

As principais configurações utilizadas são:

    DB_HOST
    DB_PORT
    DB_NAME
    DB_USER
    DB_PASSWORD

A estrutura do banco possui, entre outras, as tabelas relacionadas a clientes, endereços e pedidos.

A tabela `enderecos` possui relacionamento com a tabela `clientes`, permitindo que cada endereço seja associado ao respectivo cliente.

Entre os principais campos da tabela estão:

    id
    cliente_id
    cep
    logradouro
    numero
    complemento
    bairro
    cidade
    uf

Essa estrutura permite manter os dados de endereço relacionados aos clientes cadastrados no sistema.

---

# Integrações externas

Um dos diferenciais da API é a utilização de serviços externos para complementar as funcionalidades de logística.

Foram utilizados três serviços principais:

**ViaCEP**

Responsável pela consulta de informações de endereço a partir de um CEP.

**Nominatim**

Responsável pela geocodificação dos endereços, convertendo informações como logradouro, cidade e estado em coordenadas geográficas.

**OSRM**

Responsável pelo cálculo da rota entre dois pontos geográficos, retornando informações como distância e duração estimada.

O processo de cálculo de rota funciona da seguinte maneira:

CEP de origem e CEP de destino são informados à API.

A aplicação consulta os dois CEPs através do ViaCEP.

Com os endereços obtidos, a aplicação realiza a geocodificação utilizando o Nominatim.

As coordenadas de origem e destino são então enviadas ao OSRM.

Por fim, a API retorna a distância aproximada em quilômetros e a duração estimada da rota em minutos.

---

# Endpoints disponíveis

## Consulta inicial da API

**Método:** GET

**Endpoint:** `/`

Esse endpoint permite verificar se a API está funcionando corretamente.

Exemplo de utilização:

    curl -i "http://127.0.0.1:5002/"

Resposta esperada:

    {
      "mensagem": "API de Logística funcionando corretamente",
      "sistema": "LogControl - API de Logística",
      "status": "online"
    }

---

## Consulta de endereço por CEP

**Método:** GET

**Endpoint:** `/logistica/cep/{cep}`

Permite consultar as informações de um endereço utilizando o CEP.

Exemplo:

    curl -i "http://127.0.0.1:5002/logistica/cep/01001000"

A consulta utiliza o serviço externo ViaCEP.

A API realiza validações do CEP antes de realizar a consulta.

Entre as situações tratadas estão:

    200 – Consulta realizada com sucesso
    400 – CEP informado de forma inválida
    404 – CEP não encontrado
    502 – Falha na comunicação com o serviço externo

---

## Cálculo de rota

**Método:** GET

**Endpoint:** `/logistica/rota`

Esse endpoint permite calcular uma rota entre dois CEPs.

São utilizados os parâmetros:

    origem
    destino

Exemplo:

    curl -i "http://127.0.0.1:5002/logistica/rota?origem=01001000&destino=20040002"

A aplicação realiza a consulta dos dois CEPs, obtém suas coordenadas geográficas e posteriormente calcula a rota utilizando o OSRM.

Exemplo de retorno:

    {
      "destino": {
        "cep": "20040-002",
        "cidade": "Rio de Janeiro",
        "uf": "RJ"
      },
      "mensagem": "Rota calculada com sucesso.",
      "origem": {
        "cep": "01001-000",
        "cidade": "São Paulo",
        "uf": "SP"
      },
      "rota": {
        "distancia_km": 432.02,
        "duracao_minutos": 333
      },
      "servicos_externos": [
        "ViaCEP",
        "Nominatim",
        "OSRM"
      ]
    }

---

# Gerenciamento de endereços

A API possui operações de CRUD para gerenciamento dos endereços cadastrados.

CRUD representa as quatro operações básicas de manipulação de dados:

Cadastro, consulta, atualização e exclusão.

---

## Cadastro de endereço

**Método:** POST

**Endpoint:** `/logistica/enderecos`

Permite cadastrar um novo endereço associado a um cliente.

Exemplo:

    curl -i -X POST "http://127.0.0.1:5002/logistica/enderecos" \
    -H "Content-Type: application/json" \
    -d '{
      "cliente_id": 1,
      "cep": "01001000",
      "logradouro": "Praça da Sé",
      "numero": "100",
      "complemento": "Sala 1",
      "bairro": "Sé",
      "cidade": "São Paulo",
      "uf": "SP"
    }'

Resposta de sucesso:

    201 CREATED

A API retorna os dados do endereço cadastrado juntamente com seu identificador.

---

## Consulta de endereço cadastrado

**Método:** GET

**Endpoint:** `/logistica/enderecos/{endereco_id}`

Permite consultar um endereço através do seu identificador.

Exemplo:

    curl -i "http://127.0.0.1:5002/logistica/enderecos/2"

Resposta:

    200 OK

Exemplo de retorno:

    {
      "endereco": {
        "bairro": "Sé",
        "cep": "01001000",
        "cidade": "São Paulo",
        "cliente_id": 1,
        "complemento": "Sala 1",
        "id": 2,
        "logradouro": "Praça da Sé",
        "numero": "100",
        "uf": "SP"
      }
    }

---

## Atualização de endereço

**Método:** PUT

**Endpoint:** `/logistica/enderecos/{endereco_id}`

Permite atualizar as informações de um endereço já cadastrado.

Exemplo:

    curl -i -X PUT "http://127.0.0.1:5002/logistica/enderecos/2" \
    -H "Content-Type: application/json" \
    -d '{
      "cliente_id": 1,
      "cep": "01001000",
      "logradouro": "Praça da Sé",
      "numero": "200",
      "complemento": "Sala 2",
      "bairro": "Sé",
      "cidade": "São Paulo",
      "uf": "SP"
    }'

Resposta de sucesso:

    200 OK

A API retorna uma mensagem informando que o endereço foi atualizado e os dados atuais do registro.

---

## Exclusão de endereço

**Método:** DELETE

**Endpoint:** `/logistica/enderecos/{endereco_id}`

Permite excluir um endereço cadastrado.

Exemplo:

    curl -i -X DELETE "http://127.0.0.1:5002/logistica/enderecos/2"

Resposta de sucesso:

    200 OK

Exemplo de retorno:

    {
      "endereco_id": 2,
      "mensagem": "Endereço excluído com sucesso."
    }

A API também possui tratamento para impedir a exclusão de endereços que estejam sendo utilizados por pedidos.

---

# Validações e tratamento de erros

A API possui validações para evitar o processamento de informações inválidas.

Entre os tratamentos implementados estão:

**CEP inválido**

Caso o CEP informado não possua exatamente oito dígitos, a API retorna uma resposta de erro informando a inconsistência.

Exemplo:

    {
      "erro": "CEP de origem: O CEP deve possuir 8 dígitos."
    }

**CEP não encontrado**

Quando o CEP possui formato válido, mas não é localizado pelo serviço externo, a API retorna uma resposta `404 NOT FOUND`.

Exemplo:

    {
      "erro": "CEP de origem: CEP não encontrado."
    }

**Recurso não encontrado**

Caso seja solicitado um endereço que não esteja cadastrado no banco de dados, a API retorna uma resposta informando que o endereço não foi encontrado.

**Cliente inexistente**

O cadastro de endereço verifica a existência do cliente informado antes de realizar a inserção.

**Conflito na exclusão**

Caso um endereço esteja relacionado a um pedido, sua exclusão pode ser impedida para preservar a integridade dos dados.

---

# Documentação da API

A documentação dos endpoints foi implementada utilizando Flasgger, disponibilizando uma interface Swagger para consulta e testes.

Com a aplicação em execução, a documentação pode ser acessada através do endereço:

    http://127.0.0.1:5002/apidocs/

A especificação da API também está disponível através de:

    http://127.0.0.1:5002/apispec_1.json

O Swagger permite visualizar os endpoints, parâmetros, respostas e testar as operações diretamente pela interface.

---

# Execução do projeto

O projeto utiliza Docker para facilitar a execução da API juntamente com o banco de dados PostgreSQL.

Primeiramente, é necessário estar na pasta `logistica-api`.

Para construir a imagem da API:

    docker compose -f ../docker-compose.yml build logistica-api

Depois, para iniciar os serviços:

    docker compose -f ../docker-compose.yml up -d

Para verificar se os containers estão em execução:

    docker ps

Os principais containers utilizados são:

    logcontrol-logistica-api
    logcontrol-postgres

A API está disponibilizada na porta `5002`.

O PostgreSQL está disponibilizado na porta `5432`.

---

# Verificação do funcionamento

Após iniciar os containers, é possível verificar o funcionamento da API através do endpoint principal:

    curl -i "http://127.0.0.1:5002/"

O resultado esperado é uma resposta HTTP `200 OK`, indicando que a API está online.

Também é possível acessar diretamente a documentação Swagger:

    http://127.0.0.1:5002/apidocs/

---

# Testes realizados

Durante o desenvolvimento foram realizados testes das principais funcionalidades da aplicação.

Foram testados casos de sucesso e também situações de erro.

Consulta de rota utilizando CEPs válidos:

    origem = 01001000
    destino = 20040002

Resultado:

    200 OK

Também foi testado um CEP inexistente:

    origem = 99999999

Resultado:

    404 NOT FOUND

Foi realizada ainda a validação de um CEP com quantidade incorreta de dígitos:

    origem = 123

Resultado:

    400 BAD REQUEST

No gerenciamento de endereços foram realizados testes de cadastro, consulta, atualização e exclusão.

O cadastro retornou `201 CREATED`, a consulta retornou `200 OK`, a atualização retornou `200 OK` e a exclusão também retornou `200 OK`.

Após a exclusão, o registro foi consultado diretamente no PostgreSQL para confirmar que o endereço não permanecia na tabela.

---

# Considerações finais

O projeto demonstra a implementação de uma API REST aplicada a um cenário de logística, combinando recursos próprios da aplicação com integrações externas.

Além das operações tradicionais de CRUD, a API possui funcionalidades adicionais relacionadas à consulta de CEP, geocodificação e cálculo de rotas.

A utilização do PostgreSQL garante a persistência dos dados, enquanto o Docker proporciona maior facilidade para configuração e execução do ambiente.

A documentação através do Swagger permite uma visualização mais clara dos recursos disponibilizados pela API e facilita a realização dos testes.

O projeto representa uma implementação de MVP e poderá futuramente receber novas funcionalidades, integrações e melhorias de acordo com a evolução das necessidades do sistema.

---

# Autor

Tiago Presotti

Projeto desenvolvido MVP da pós-graduação em Desenvolvimento Full Stack da PUC-Rio.