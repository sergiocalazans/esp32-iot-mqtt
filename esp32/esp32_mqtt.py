import network
from umqtt.simple import MQTTClient
import machine
import time
import json
import dht
import random

# ==== CONFIGURACOES ====
SSID = "Visitantes" 
SENHA = "" 
BROKER = "test.mosquitto.org"
PORTA = 1883
CLIENT_ID = "esp32-grupo12"
TOPICOS_PUBLICAR = ["grupo12/sala1/dados", "grupo12/sala2/dados", "grupo12/sala3/dados"]
TOPICO_ASSINAR = "grupo12/pc/comandos"
QOS = 1

# Leds
led_estado = False
led = machine.Pin(2, machine.Pin.OUT)
led1 = machine.Pin(12, machine.Pin.OUT)
led2 = machine.Pin(14, machine.Pin.OUT)
led3 = machine.Pin(27, machine.Pin.OUT)

# Buzzer
buzzer = machine.PWM(machine.Pin(18))
buzzer.duty(0)

# HC-SR04
trig = machine.Pin(2, machine.Pin.OUT)
echo = machine.Pin(4, machine.Pin.IN)

# DHT11
sensor = dht.DHT11(machine.Pin(15))

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando ao Wi-Fi...")
        wlan.connect(SSID, SENHA)
        tentativas = 0
        while not wlan.isconnected() and tentativas < 20:
            time.sleep(1)
            tentativas += 1
            print(f" Tentativa {tentativas}/20...")
    if wlan.isconnected():
        print(f"Wi-Fi conectado! IP: {wlan.ifconfig()[0]}")
        return True
    else:
        print("ERRO: Nao foi possivel conectar ao Wi-Fi")
        return False
    
def callback_mensagem(topico, mensagem):
    global led_estado, encerrar
    topico = topico.decode("utf-8")
    payload = mensagem.decode("utf-8")
    print(f"[MICRO] Recebido em '{topico}': {payload}")
    
    try:
        dados = json.loads(payload)
        comando = dados.get("comando", "")
        
        if comando == "led_on":
            led.value(1)
            led_estado = True
            print("[MICRO] LED ligado!")
            publicar_estado()
        elif comando == "led_off":
            led.value(0)
            led_estado = False
            print("[MICRO] LED desligado!")
            publicar_estado()
        elif comando == "status":
            publicar_dados_sensor()
            time.sleep(1)
        else:
            print(f"[MICRO] Comando desconhecido: {comando}")
    except Exception as e:
        print(f"[MICRO] Erro ao processar: {e}")
        
def publicar_estado():
    estado = "ligado" if led_estado else "desligado"
    msg = json.dumps({"led": estado})
    client.publish(TOPICOS_PUBLICAR[2], msg, qos=QOS) 
    print(f"[MICRO] Publicado: {msg}")

def emitir_som(frequencia, duracao):
    buzzer.freq(frequencia)
    buzzer.duty(512) 
    time.sleep(duracao)
    buzzer.duty(0)

def publicar_dados_sensor():
    try:
        
        led1.value(0)
        led2.value(0)
        led3.value(0)
        
        sensor.measure() 
        led.value(1)
        
        dados1 = {
            "sensor": "dht11",
            "temperatura": sensor.temperature(),
            "umidade": sensor.humidity(),
            "status": "enviado"
        }
        client.publish("grupo12/sala1/dados", json.dumps(dados1), qos=QOS)
        led.value(0)

        dist = medir_distancia()
        cor_led = ""
        
        if dist < 100:
            led1.value(1)
            cor_led = "Vermelho (Perigo)"
            
            for _ in range(3):
                emitir_som(640, 4)
                time.sleep(0.05)
                
            time.sleep(0.5)
            led1.value(0)
            
        elif 200 < dist < 300:
            led2.value(1)
            cor_led = "Amarelo (Atencao)"
            emitir_som(880, 0.2)
            time.sleep(0.5)
            led2.value(0)
            
        elif dist > 300:
            led3.value(1)
            cor_led = "Verde (Seguro)"
            emitir_som(1500, 0.1)
            time.sleep(0.5)
            led3.value(0)
            
        dados2 = {
            "sensor": "hc-sr04",
            "distancia": dist,
            "led_status": cor_led
        }
        client.publish(TOPICOS_PUBLICAR[1], json.dumps(dados2), qos=QOS)
            
    except Exception as e:
        print(f"Erro: {e}")
        buzzer.duty(0)
        
if not conectar_wifi():
    print("Abortando: sem Wi-Fi.")
    raise SystemExit

print("[MICRO] Conectando ao broker MQTT...")
client = MQTTClient(CLIENT_ID, BROKER, port=PORTA, keepalive=60)
client.set_callback(callback_mensagem)
client.connect(clean_session=False) 
print(f"[MICRO] Conectado a {BROKER}")

client.subscribe(TOPICO_ASSINAR, qos=QOS)
print(f"[MICRO] Inscrito: {TOPICO_ASSINAR}")

def medir_distancia():
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    while echo.value() == 0:
        pulse_start = time.ticks_us()

    while echo.value() == 1:
        pulse_end = time.ticks_us()

    pulse_duration = time.ticks_diff(pulse_end, pulse_start)

    distancia = (pulse_duration / 2) * 0.0343

    return distancia

def medir_temperatura():
    try:
        sensor.measure()
        return {"temperatura": sensor.temperature(), "umidade": sensor.humidity()}
    except:
        return {"temperatura": 0, "umidade": 0}

contador = 0
try:
    while True:
        dist = medir_distancia()
        client.check_msg()

        contador += 1
        if contador >= 10:
            publicar_dados_sensor()
            contador = 0
        
        time.sleep(1)

except KeyboardInterrupt:
    print("\n[MICRO] Interrompido.")
finally:
    client.disconnect()
    