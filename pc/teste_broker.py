# teste_broker.py
import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc, properties):
  if rc == 0:
    print("Conectado ao broker com sucesso!")
  else:
    print(f"Falha na conexao. Codigo: {rc}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
print("Conectando ao broker test.mosquitto.org...")
client.connect("test.mosquitto.org", 1883, 60)
client.loop_start()

time.sleep(3)
client.disconnect()
print("Desconectado.")
