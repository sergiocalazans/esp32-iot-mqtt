# Relatório Técnico — Sistema IoT de Monitoramento de Reservatório com ESP32 e MQTT

**Instituição:** Pontifícia Universidade Católica do Paraná (PUCPR)  
**Curso:** Ciência da Computação  
**Disciplina:** Experiência Criativa: Criando Soluções Computacionais  
**Período:** 3º período  
**Ano:** 2026

## 1. Introdução

O projeto apresenta um protótipo de **monitoramento de reservatório de água**, desenvolvido com o microcontrolador ESP32 e comunicação via protocolo MQTT. A solução coleta dados de temperatura e umidade por meio de um sensor DHT11 e utiliza o sensor ultrassônico HC-SR04 para medir a distância até uma superfície, permitindo representar condições associadas ao nível de água do reservatório.

A sinalização local é realizada por LEDs e buzzer. Os dados são enviados pela rede Wi-Fi a um broker MQTT e recebidos por uma aplicação Python no computador, que também pode transmitir comandos ao microcontrolador.

## 2. Objetivos

- Integrar sensores reais ao ESP32 com MicroPython.
- Transmitir leituras e estados em mensagens JSON utilizando MQTT.
- Implementar comunicação de comandos entre computador e microcontrolador.
- Utilizar **QoS 1** na publicação e na assinatura de tópicos e configurar sessões persistentes.
- Organizar a comunicação por múltiplos tópicos, utilizando assinatura com wildcard.
- Sinalizar faixas de distância por LEDs e buzzer.

## 3. Materiais e tecnologias

| Componente ou tecnologia     | Utilização                                              |
| ---------------------------- | ------------------------------------------------------- |
| ESP32                        | Processamento, conexão Wi-Fi e controle dos periféricos |
| DHT11                        | Leitura de temperatura e umidade                        |
| HC-SR04                      | Medição ultrassônica de distância                       |
| LEDs                         | Sinalização visual das faixas de distância              |
| Buzzer                       | Sinalização sonora                                      |
| Protoboard e conexões        | Montagem do circuito                                    |
| MicroPython e `umqtt.simple` | Programa embarcado e comunicação MQTT                   |
| Python e `paho-mqtt`         | Aplicação no computador                                 |
| Broker `test.mosquitto.org`  | Intermediação das mensagens MQTT                        |
| JSON                         | Formato de intercâmbio de dados                         |

## 4. Arquitetura e funcionamento

O ESP32 conecta-se à rede Wi-Fi e ao broker MQTT. O computador estabelece uma segunda conexão com o mesmo broker. O envio e o recebimento das mensagens seguem o modelo _publish/subscribe_, sem conexão direta entre os dois programas.

```text
Sensores DHT11 e HC-SR04
            |
            v
     ESP32 / MicroPython ----> LEDs e buzzer
            |
      Wi-Fi / MQTT
            |
            v
  Broker test.mosquitto.org
            ^
            |
      Python no computador
  (recepção e envio de comandos)
```

### 4.1. Tópicos MQTT

Conforme os arquivos de código disponibilizados para publicação:

| Tópico                | Finalidade                                                   |
| --------------------- | ------------------------------------------------------------ |
| `grupo12/pc/comandos` | Comandos publicados pelo computador e recebidos pelo ESP32   |
| `grupo12/sala1/dados` | Dados de temperatura e umidade do DHT11                      |
| `grupo12/sala2/dados` | Distância e classificação do alerta do HC-SR04               |
| `grupo12/sala3/dados` | Estado do LED de controle                                    |
| `grupo12/+/dados`     | Assinatura do computador que recebe mensagens das três salas |

O caractere `+` representa um único nível variável do tópico. As mensagens são publicadas com **QoS 1**, modalidade que prevê entrega _pelo menos uma vez_, podendo haver duplicatas. Os clientes também são configurados com `clean_session=False`, para utilização de sessões persistentes conforme o suporte do broker.

### 4.2. Comandos disponíveis

| Comando   | Ação                                            |
| --------- | ----------------------------------------------- |
| `led_on`  | Liga o LED de controle e publica seu estado     |
| `led_off` | Desliga o LED de controle e publica seu estado  |
| `status`  | Solicita a publicação das leituras dos sensores |
| `sair`    | Encerra a aplicação do computador               |

Exemplo de comando transmitido:

```json
{ "comando": "status" }
```

Exemplos ilustrativos da estrutura das respostas, **não medições registradas no experimento**:

```json
{ "sensor": "dht11", "temperatura": 25, "umidade": 60, "status": "enviado" }
```

```json
{ "sensor": "hc-sr04", "distancia": 85.5, "led_status": "Vermelho (Perigo)" }
```

## 5. Desenvolvimento dos desafios

### 5.1. Desafio 1 — Sensor real

Foi implementada a leitura de temperatura e umidade por meio do sensor DHT11. Durante os testes, também foi integrado o sensor ultrassônico HC-SR04, utilizado para medir a distância. As leituras foram estruturadas em mensagens e disponibilizadas ao programa Python no computador.

O relatório original registra uma dificuldade com o DHT11 inicialmente utilizado no kit, que precisou ser substituído por outro componente para viabilizar os testes.

![Protótipo do circuito com sensores](https://raw.githubusercontent.com/sergiocalazans/esp32-iot-mqtt/main/docs/img/prototipo.jpg)

_Figura 1 — Montagem do protótipo com sensores. Adicionar imagem correspondente._

![Leituras recebidas no computador](https://raw.githubusercontent.com/sergiocalazans/esp32-iot-mqtt/main/img/resultado-servidor.jpg)

_Figura 2 — Mensagens recebidas pela aplicação Python. Adicionar captura correspondente._

### 5.2. Desafio 2 — QoS e persistência

A comunicação foi configurada para utilizar QoS 1 tanto na publicação quanto na assinatura dos tópicos. Esse nível oferece confirmação de entrega no protocolo, com a possibilidade de retransmissão e recebimento de mensagens duplicadas.

A configuração de sessão persistente foi aplicada aos clientes MQTT. No computador, o código verifica se uma sessão anterior foi restaurada por meio de `session_present` e define uma política de tentativa de reconexão. Isso não constitui, isoladamente, comprovação de que todas as mensagens tenham sido recuperadas após uma desconexão; tal comportamento depende das condições de sessão, assinatura e broker.

![Circuito utilizado no segundo desafio](https://raw.githubusercontent.com/sergiocalazans/esp32-iot-mqtt/main/img/prototipo-2.jpg)

_Figura 3 — Montagem utilizada no desafio de QoS e persistência. Adicionar imagem correspondente._

### 5.3. Desafio 3 — Múltiplos sensores e tópicos

Foram utilizados tópicos distintos para transmitir os dados do DHT11, do HC-SR04 e do estado do LED. A aplicação do computador realiza uma única assinatura com wildcard (`grupo12/+/dados`) e identifica a origem da mensagem a partir do nome do tópico.

A estrutura permite receber e apresentar informações de diferentes categorias sem cadastrar individualmente cada tópico na aplicação Python.

![Mensagens dos diferentes tópicos](https://raw.githubusercontent.com/sergiocalazans/esp32-iot-mqtt/main/img/mensagens.png)

_Figura 4 — Recepção das mensagens de múltiplos tópicos. Adicionar captura correspondente._

## 6. Monitoramento do reservatório e alertas

O HC-SR04 fornece uma medida de distância. No contexto do protótipo, essa leitura é usada para representar condições do nível de água do reservatório. A correspondência entre distância e nível depende da posição de instalação do sensor e da geometria do recipiente.

No código disponibilizado, as condições de acionamento são:

| Distância medida                    | Sinalização                 | Classificação |
| ----------------------------------- | --------------------------- | ------------- |
| Menor que 100 cm                    | LED vermelho e buzzer       | Perigo        |
| Maior que 200 cm e menor que 300 cm | LED amarelo e buzzer        | Atenção       |
| Maior que 300 cm                    | LED verde e buzzer          | Seguro        |
| Demais valores                      | Sem classificação explícita | Não definida  |

**Observação técnica:** os intervalos entre 100 e 200 cm e alguns valores de fronteira não estão contemplados nas condições do código. As classificações acima reproduzem a lógica implementada e não representam uma calibração validada do reservatório.

![Montagem completa do protótipo](https://raw.githubusercontent.com/sergiocalazans/esp32-iot-mqtt/main/img/prototipo-final.png)

_Figura 5 — Protótipo físico completo._

### 6.1. Demonstração em vídeo

**[▶ Assistir à demonstração do protótipo](https://youtube.com/shorts/oOtab-wPSVg?si=J7D00AKEp8U1KYNm)**

## 7. Testes e resultados

O relatório da atividade documenta a montagem do circuito, o recebimento de mensagens no computador e a utilização de diferentes tópicos. O sistema foi apresentado como um protótipo capaz de monitorar temperatura, umidade e distância, além de sinalizar condições por LEDs e buzzer.

Durante o desenvolvimento, houve necessidade de correções sucessivas no código. O documento original também relata um erro intermitente `-1` no ambiente Wokwi quando três comandos eram enviados simultaneamente. A causa não foi identificada naquele registro.

Não foram apresentados resultados quantitativos de latência, taxa de entrega ou precisão dos sensores; portanto, não é possível concluir esses indicadores a partir da documentação disponível.

## 8. Limitações e melhorias futuras

- **Pinos:** no código fornecido, o GPIO 2 é compartilhado entre o LED de controle e o sinal `trig` do HC-SR04, o que merece revisão antes de uma nova montagem.
- **Timeout:** a rotina de medição do HC-SR04 aguarda pulsos sem limite de tempo explícito, podendo ficar bloqueada em caso de ausência de resposta.
- **Faixas de alerta:** definir limites contínuos, sem lacunas, e calibrá-los de acordo com as dimensões reais do reservatório.
- **Comunicação:** avaliar recuperação de conexão e comportamento da sessão persistente em testes controlados de desconexão.
- **Segurança:** o broker público utiliza a porta 1883 sem criptografia; para aplicações reais, considerar autenticação e TLS.
- **Documentação:** adicionar fotografias, capturas de terminal e vídeos da execução.

## 9. Considerações finais

O projeto permitiu aplicar conceitos de Internet das Coisas e sistemas embarcados por meio da integração entre ESP32, sensores, atuadores e uma aplicação Python. A utilização de MQTT demonstrou o intercâmbio de mensagens entre dispositivos por tópicos, incluindo QoS 1, sessões persistentes e assinatura com wildcard.

A implementação também evidenciou desafios práticos relacionados ao funcionamento de componentes físicos, à depuração de código e à estabilidade da comunicação. O protótipo constitui uma base acadêmica para evoluções futuras em monitoramento remoto de reservatórios.
