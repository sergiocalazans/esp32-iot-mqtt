# Monitoramento e Controle IoT com ESP32 e MQTT

Projeto acadêmico desenvolvido no **3º período de Ciência da Computação da PUCPR**, na disciplina **Experiência Criativa: Criando Soluções Computacionais**. O sistema integra um microcontrolador ESP32, sensores e atuadores com uma aplicação Python no computador, utilizando o protocolo MQTT para troca de mensagens em JSON.

## Objetivo

Explorar conceitos de Internet das Coisas (IoT), sistemas embarcados e comunicação no modelo _publish/subscribe_, permitindo coletar medições, publicar dados em tópicos MQTT e enviar comandos remotamente ao ESP32.

## Tecnologias e componentes

- **Hardware:** ESP32, sensor DHT11 (temperatura e umidade), sensor ultrassônico HC-SR04 (distância), LEDs e buzzer.
- **ESP32:** MicroPython, `umqtt.simple`, `machine`, `network` e `dht`.
- **Computador:** Python 3 e biblioteca `paho-mqtt`.
- **Comunicação:** MQTT, JSON, Wi-Fi e broker público `test.mosquitto.org` (porta 1883).

## Funcionalidades implementadas no código

- Leitura de temperatura e umidade com DHT11.
- Medição de distância com HC-SR04.
- Alertas locais por LEDs e buzzer conforme faixas de distância.
- Publicação de dados dos sensores em tópicos distintos.
- Recepção de comandos `led_on`, `led_off` e `status`.
- Comunicação com **QoS 1** e configuração de sessões MQTT persistentes.
- Assinatura com wildcard `+` na aplicação do computador.
- Tentativa de reconexão automática configurada no cliente Python do computador.

## Arquitetura

```text
                    Broker MQTT público
                     test.mosquitto.org
                         porta 1883
                         /        \
                        /          \
                  Wi-Fi /            \ Rede
                      /              \
                 ESP32               Computador
              (MicroPython)          (Python)
              umqtt.simple           paho-mqtt
                /     \                   |
         DHT11 /       \ HC-SR04          | Terminal:
             /         \                 | comandos e dados
        LEDs e buzzer (atuadores)
```

O computador publica comandos no tópico `grupo12/pc/comandos`; o ESP32 assina esse tópico e publica informações dos sensores nos tópicos `grupo12/sala1/dados` e `grupo12/sala2/dados`. O tópico `grupo12/sala3/dados` é utilizado para publicar o estado do LED. O computador assina `grupo12/+/dados`, recebendo mensagens das três salas.

### Tópicos MQTT

| Tópico                | Publicador | Conteúdo                                          |
| --------------------- | ---------- | ------------------------------------------------- |
| `grupo12/pc/comandos` | Computador | Comandos JSON destinados ao ESP32                 |
| `grupo12/sala1/dados` | ESP32      | Temperatura e umidade do DHT11                    |
| `grupo12/sala2/dados` | ESP32      | Distância do HC-SR04 e descrição do alerta        |
| `grupo12/sala3/dados` | ESP32      | Estado do LED                                     |
| `grupo12/+/dados`     | —          | Assinatura com wildcard utilizada pelo computador |

### Exemplos de mensagens

Comando enviado pelo computador:

```json
{ "comando": "led_on" }
```

Dados de temperatura e umidade (exemplo ilustrativo):

```json
{ "sensor": "dht11", "temperatura": 25, "umidade": 60, "status": "enviado" }
```

Dados de distância (exemplo ilustrativo):

```json
{ "sensor": "hc-sr04", "distancia": 85.0, "led_status": "Vermelho (Perigo)" }
```

## Estrutura do projeto

```text
esp32-iot-mqtt/
├── esp32/
│   └── esp32_mqtt.py       # Programa do microcontrolador
├── pc/
│   ├── pc_mqtt.py          # Cliente MQTT para comandos e recepção
│   └── teste_broker.py     # Teste de conexão ao broker
├── docs/
│   └── imagens/            # Espaço reservado para fotos e diagramas
├── .gitignore
├── requirements.txt
└── README.md
```

## Como executar

### 1. Preparar o computador

Instale Python 3 e execute, na raiz do repositório:

```bash
python -m pip install -r requirements.txt
python pc/teste_broker.py
```

O teste deve indicar se a conexão com o broker foi estabelecida. Depois, execute:

```bash
python pc/pc_mqtt.py
```

### 2. Preparar o ESP32

1. Grave uma versão compatível do firmware MicroPython na placa.
2. Abra `esp32/esp32_mqtt.py` no Thonny e selecione o interpretador MicroPython (ESP32).
3. Configure `SSID` e `SENHA` de uma rede Wi-Fi **2,4 GHz**; evite inserir senhas reais em arquivos versionados.
4. Confirme a pinagem conforme a montagem física e instale `umqtt.simple` no dispositivo, caso necessário.
5. Execute o script no ESP32 e acompanhe a saída serial no Thonny.
6. No terminal do computador, envie `led_on`, `led_off` ou `status`.

> **Atenção:** antes de executar no hardware, revise as ressalvas de pinagem e leitura ultrassônica indicadas abaixo. O código fornecido usa o GPIO 2 tanto para o LED quanto para o pino TRIG do HC-SR04.

## Alertas por distância

As condições programadas no ESP32 são:

| Distância                           | Sinalização                               |
| ----------------------------------- | ----------------------------------------- |
| Menor que 100 cm                    | LED vermelho e três sinais sonoros de 4 s |
| Maior que 200 cm e menor que 300 cm | LED amarelo e sinal de 0,2 s              |
| Maior que 300 cm                    | LED verde e sinal de 0,1 s                |

As distâncias entre 100 e 200 cm, inclusive, e os limites exatos de 300 cm não recebem classificação nessas condições. A leitura do HC-SR04 também não possui timeout; uma ausência de eco pode bloquear a execução.

## Limitações e cuidados

- **GPIO compartilhado:** o GPIO 2 está configurado para o LED e o TRIG do HC-SR04; é necessário corrigir o conflito antes de uma montagem confiável.
- **Leitura do ultrassônico:** os loops de espera do ECHO não possuem timeout.
- **Segurança:** a porta 1883 do broker público não utiliza TLS nem autenticação; use apenas dados não sensíveis e, para aplicações reais, prefira broker autenticado e conexão criptografada.
- **Identificadores e tópicos:** os IDs `esp32-grupo12` e `pc-grupo12` e os tópicos `grupo12/...` devem ser alterados se houver conflitos com outras instalações.
- **Sessões persistentes:** o código solicita sessões persistentes, mas não demonstra testes documentados de entrega após desconexões.
- **Execução:** o projeto depende de conectividade com o broker público e de montagem física compatível com a pinagem.

## Aprendizados

O projeto aborda integração entre software e hardware, leitura de sensores, acionamento de atuadores, comunicação assíncrona com MQTT, estruturação de mensagens em JSON e conceitos de QoS, tópicos e persistência de sessão.

## Contexto acadêmico

Desenvolvido a partir de uma atividade da disciplina **Experiência Criativa: Criando Soluções Computacionais**, da **Pontifícia Universidade Católica do Paraná (PUCPR)**. A proposta da atividade envolvia comunicação MQTT entre Python e MicroPython e desafios de sensores reais, QoS e múltiplos sensores e atuadores.

## Referências

- [Documentação do MicroPython](https://docs.micropython.org/)
- [Documentação do Eclipse Paho MQTT para Python](https://eclipse.dev/paho/files/paho.mqtt.python/html/)
- [Protocolo MQTT](https://mqtt.org/)
- [Broker público Mosquitto](https://test.mosquitto.org/)
- [Thonny IDE](https://thonny.org/)
