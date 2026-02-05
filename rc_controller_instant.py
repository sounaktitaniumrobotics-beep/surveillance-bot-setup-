import paho.mqtt.client as mqtt
import keyboard
import time

# MQTT Configuration
BROKER = "1887637a30c2432683efd36d80813f78.s1.eu.hivemq.cloud"
PORT = 8883
USERNAME = "titaniumrobotics"
PASSWORD = "Sapt090059#"
TOPIC = "rccar/control"

# ========== SPEED CONFIGURATION ==========
CONSTANT_SPEED = 60         # Medium speed (0-100, try 50-70 for medium)
CONSTANT_STEERING = 70      # Steering strength (0-100, try 60-80)
UPDATE_RATE = 0.02          # 50Hz update rate for instant response
# =========================================

# Control variables
throttle = 0
steering = 0

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to MQTT Broker! Return code: {reason_code}")
    if reason_code == 0:
        print("Successfully connected!")
        print("\n" + "="*50)
        print("RC CAR CONTROLS - INSTANT CONSTANT SPEED MODE")
        print("="*50)
        print("W        - Forward (instant " + str(CONSTANT_SPEED) + "% speed)")
        print("S        - Backward (instant " + str(CONSTANT_SPEED) + "% speed)")
        print("A        - Left Turn")
        print("D        - Right Turn")
        print("SPACE    - Stop")
        print("ESC      - Quit")
        print("="*50)
        print(f"\nSpeed Settings:")
        print(f"  Constant Speed: {CONSTANT_SPEED}%")
        print(f"  Steering Power: {CONSTANT_STEERING}%")
        print("="*50 + "\n")
    else:
        print(f"Failed to connect, return code {reason_code}")

def send_command(client):
    message = f"{throttle},{steering}"
    result = client.publish(TOPIC, message, qos=1)
    
    # Display status with directional indicator
    direction = ""
    if throttle > 0 and steering == 0:
        direction = "↑ FORWARD"
    elif throttle < 0 and steering == 0:
        direction = "↓ BACKWARD"
    elif throttle > 0 and steering > 0:
        direction = "↗ FORWARD-RIGHT"
    elif throttle > 0 and steering < 0:
        direction = "↖ FORWARD-LEFT"
    elif throttle < 0 and steering > 0:
        direction = "↘ BACKWARD-RIGHT"
    elif throttle < 0 and steering < 0:
        direction = "↙ BACKWARD-LEFT"
    elif throttle == 0 and steering > 0:
        direction = "→ RIGHT TURN"
    elif throttle == 0 and steering < 0:
        direction = "← LEFT TURN"
    elif throttle == 0 and steering == 0:
        direction = "● STOPPED"
    
    print(f"T: {throttle:4}% | S: {steering:4}% | {direction:20}", end='\r')

def main():
    global throttle, steering
    
    # Setup MQTT client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set()
    client.on_connect = on_connect
    
    print("Connecting to MQTT broker...")
    try:
        client.connect(BROKER, PORT, 60)
    except Exception as e:
        print(f"Connection failed: {e}")
        return
    
    client.loop_start()
    time.sleep(2)
    
    print("\nRC Car Control Ready!")
    print("Press keys for INSTANT response at constant speed...\n")
    
    try:
        while True:
            # INSTANT THROTTLE CONTROL - No gradual acceleration
            if keyboard.is_pressed('w'):
                throttle = CONSTANT_SPEED      # Instant forward at constant speed
            elif keyboard.is_pressed('s'):
                throttle = -CONSTANT_SPEED     # Instant backward at constant speed
            else:
                throttle = 0                    # Instant stop when released
            
            # INSTANT STEERING CONTROL - No gradual turning
            if keyboard.is_pressed('d'):
                steering = CONSTANT_STEERING    # Instant right turn
            elif keyboard.is_pressed('a'):
                steering = -CONSTANT_STEERING   # Instant left turn
            else:
                steering = 0                    # Instant center when released
            
            # Emergency stop
            if keyboard.is_pressed('space'):
                throttle = 0
                steering = 0
                print("\n*** EMERGENCY STOP ***" + " "*20, end='\r')
            
            # Quit
            if keyboard.is_pressed('esc'):
                throttle = 0
                steering = 0
                send_command(client)
                print("\n\nStopping car and exiting...")
                break
            
            send_command(client)
            time.sleep(UPDATE_RATE)
            
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # Send stop command before disconnecting
        throttle = 0
        steering = 0
        send_command(client)
        time.sleep(0.5)
        client.loop_stop()
        client.disconnect()
        print("Disconnected safely.")

if __name__ == "__main__":
    main()
