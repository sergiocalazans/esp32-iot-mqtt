import paho.mqtt.client as mqtt
import time
import json

# ---- Configuracoes ----
BROKER = "test.mosquitto.org"
PORTA = 1883
TOPICO_PUBLICAR = "grupo12/pc/comandos"
TOPICO_ASSINAR = "grupo12/+/dados"
CLIENT_ID = "pc-grupo12"
QOS = 1


# =========================
# CALLBACKS
# =========================
def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("\n[PC] Conectado ao broker MQTT!")

        if flags.session_present:
            print("[PC] Sessão persistente restaurada ✔")
        else:
            print("[PC] Nova sessão criada")

        client.subscribe(TOPICO_ASSINAR, qos=1)
        print(f"[PC] Inscrito no tópico: {TOPICO_ASSINAR}")
    else:
        print(f"[PC] Falha na conexão, código: {rc}")


def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    
    topico_partes = msg.topic.split('/')
    sala = topico_partes[1] if len(topico_partes) > 1 else "desconhecida"

    print(f"\n>>> MENSAGEM RECEBIDA DA {sala.upper()} <<<")
    
    try:
        dados = json.loads(payload)
        sensor_nome = dados.get("sensor", "N/A")
        print(f"Sensor: {sensor_nome}")
        
        if sensor_nome == "dht11":
            print(f" -> Temp: {dados.get('temperatura')}°C")
            print(f" -> Umid: {dados.get('umidade')}%")
        
        elif sensor_nome == "hc-sr04":
            print(f" -> Distância: {dados.get('distancia')}cm")
            print(f" -> Estado do Alerta: {dados.get('led_status')}")
            
    except json.JSONDecodeError:
        print(f" -> Payload (texto): {payload}")
    
    print("-" * 30)

def on_disconnect(client, userdata, flags, rc, properties):
    print(f"\n[PC] Desconectado (rc={rc})")

    if rc != 0:
        print("[PC] Tentando reconectar automaticamente...")


# =========================
# PROGRAMA PRINCIPAL
# =========================
def main():
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=CLIENT_ID,
        clean_session=False  # ESSENCIAL para persistência
    )

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    # Reconexão automática
    client.reconnect_delay_set(min_delay=1, max_delay=5)

    print(f"[PC] Conectando a {BROKER}...")

    try:
        client.connect(BROKER, PORTA, 60)
    except Exception as e:
        print(f"[PC] Erro ao conectar: {e}")
        return

    client.loop_start()
    time.sleep(1)

    print("\n--- COMANDOS: led_on | led_off | status | sair ---\n")

    try:
        while True:
            comando = input("[PC] Digite um comando: ").strip()

            if comando.lower() == "sair":
                print("[PC] Encerrando aplicação...")
                break

            if comando:
                mensagem = json.dumps({"comando": comando})

                info = client.publish(
                    TOPICO_PUBLICAR,
                    mensagem,
                    qos=QOS
                )

                info.wait_for_publish()

                if info.rc == mqtt.MQTT_ERR_SUCCESS:
                    print(f"[PC] Publicado com QoS 1 ✔: {mensagem}")
                else:
                    print("[PC] Erro ao publicar mensagem")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n[PC] Interrompido pelo usuário")

    finally:
        client.loop_stop()
        client.disconnect()
        print("[PC] Desconectado do broker")


if __name__ == "__main__":
    main()