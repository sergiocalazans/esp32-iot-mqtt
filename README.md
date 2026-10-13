<div align="center">

![Banner do projeto ESP32 IoT](https://raw.githubusercontent.com/sergiocalazans/esp32-iot-mqtt/main/img/banner.png)

# Monitoramento de Reservatório com ESP32 e MQTT

**Projeto acadêmico de Internet das Coisas (IoT) com MicroPython, Python e comunicação MQTT.**

</div>

## Sobre o projeto

Desenvolvido no **3º período de Ciência da Computação da PUCPR**, na disciplina **Experiência Criativa: Criando Soluções Computacionais**, o projeto apresenta um protótipo de monitoramento de reservatório de água. Um **ESP32** integra sensores e atuadores, enquanto uma aplicação **Python** no computador recebe medições e envia comandos pela rede usando o protocolo **MQTT**.

O sensor **HC-SR04** mede a distância até a superfície, usada como referência para o nível da água; o **DHT11** coleta temperatura e umidade do ambiente. LEDs e buzzer fornecem alertas locais conforme as faixas de distância configuradas.

## Protótipo final

![Fotografia do protótipo final com ESP32 e sensores](https://raw.githubusercontent.com/sergiocalazans/esp32-iot-mqtt/main/img/prototipo-final.png)

_Montagem física do protótipo com ESP32, sensores DHT11 e HC-SR04, LEDs e buzzer._

## Demonstração em vídeo

**[▶ Assistir à demonstração do protótipo](https://youtube.com/shorts/oOtab-wPSVg?si=J7D00AKEp8U1KYNm)**

## Funcionalidades

- Leitura de **temperatura e umidade** com DHT11.
- Medição de **distância** com HC-SR04 para acompanhamento do nível de água.
- Sinalização por **LEDs e buzzer** de acordo com faixas de distância.
- Envio de dados em **JSON** por tópicos MQTT.
- Recebimento de comandos remotos (`led_on`, `led_off` e `status`).
- Comunicação MQTT com **QoS 1**, sessões configuradas como persistentes e assinatura de múltiplos tópicos com **wildcard**.

## Tecnologias e componentes

| Categoria              | Tecnologias e componentes    |
| ---------------------- | ---------------------------- |
| Microcontrolador       | ESP32                        |
| Linguagens             | MicroPython e Python         |
| Comunicação            | Wi-Fi, MQTT e JSON           |
| Bibliotecas            | `umqtt.simple` e `paho-mqtt` |
| Sensores               | DHT11 e HC-SR04              |
| Atuadores              | LEDs e buzzer                |
| Broker de demonstração | `test.mosquitto.org`         |

## Comunicação MQTT

O ESP32 publica as leituras dos sensores e os estados do dispositivo no broker MQTT. A aplicação Python se inscreve nos tópicos de dados, apresenta as mensagens recebidas e publica comandos para o ESP32.

| Tópico                | Finalidade                               |
| --------------------- | ---------------------------------------- |
| `grupo12/sala1/dados` | Temperatura e umidade (DHT11)            |
| `grupo12/sala2/dados` | Distância e estado do alerta (HC-SR04)   |
| `grupo12/sala3/dados` | Estado do LED                            |
| `grupo12/pc/comandos` | Comandos enviados pelo computador        |
| `grupo12/+/dados`     | Assinatura de dados de múltiplos tópicos |

## Estrutura do repositório

```text
esp32-iot-mqtt/
├── esp32/
│   └── esp32_mqtt.py
├── pc/
│   ├── pc_mqtt.py
│   └── teste_broker.py
├── docs/
│   └── RELATORIO.md
├── img/
├── requirements.txt
├── .gitignore
└── README.md
```

## Como executar

1. Instale o Python no computador e as dependências com `pip install -r requirements.txt`.
2. Configure o ESP32 com firmware **MicroPython** e a biblioteca `umqtt.simple`.
3. Ajuste as configurações de Wi-Fi no arquivo `esp32/esp32_mqtt.py` e confirme os pinos da montagem.
4. Execute o código do ESP32 pelo **Thonny**.
5. No computador, verifique a conexão com `python pc/teste_broker.py` e execute `python pc/pc_mqtt.py`.
6. Utilize os comandos `led_on`, `led_off` e `status` no terminal.

> **Atenção:** o projeto utiliza um broker público na porta 1883, sem criptografia, apenas para fins didáticos. Antes de executar no hardware, revise o uso compartilhado do GPIO 2 pelo LED e pelo TRIG do HC-SR04 e a ausência de timeout na leitura do sensor ultrassônico.

## Documentação técnica

O detalhamento do desenvolvimento, das atividades realizadas e dos resultados está disponível no documento separado:

**📄 [Acessar o relatório técnico](https://github.com/sergiocalazans/esp32-iot-mqtt/main/docs/RELATORIO.md)**

---

## Referências

- [MicroPython — Documentação oficial](https://docs.micropython.org/)
- [Eclipse Paho MQTT Python](https://eclipse.dev/paho/files/paho.mqtt.python/html/)
- [MQTT — Site oficial](https://mqtt.org/)
- [Mosquitto — Broker público de testes](https://test.mosquitto.org/)
