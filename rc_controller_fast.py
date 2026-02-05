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
ACCELERATION_RATE = 10      # Increase from 5 to 10 for faster acceleration
DECELERATION_RATE = 8       # Increase from 3 to 8 for faster deceleration
STEERING_RATE = 10          # Increase from 5 to 10 for faster steering
STEERING_RETURN_RATE = 10   # Increase from 5 to 10 for faster centering
UPDATE_RATE = 0.03          # Decrease from 0.05 to 0.03 for more responsive (33Hz)
# =========================================

# Control variables
throttle = 0
steering = 0

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to MQTT Broker! Return code: {reason_code}")
    if reason_code == 0:
        print("Successfully connected!")
        print("\n" + "="*50)
        print("RC CAR CONTROLS")
        print("="*50)
        print("W/S      - Forward/Backward (Faster acceleration)")
        print("A/D      - Left/Right")
        print("SPACE    - Emergency Stop")
        print("ESC      - Quit")
        print("="*50)
        print(f"\nSpeed Settings:")
        print(f"  Acceleration Rate: {ACCELERATION_RATE}")
        print(f"  Update Rate: {int(1/UPDATE_RATE)}Hz")
        print("="*50 + "\n")
    else:
        print(f"Failed to connect, return code {reason_code}")

def on_publish(client, userdata, mid, reason_code, properties):
    pass

def send_command(client):
    message = f"{throttle},{steering}"
    result = client.publish(TOPIC, message, qos=1)
    print(f"Throttle: {throttle:4}% | Steering: {steering:4}% | Status: {'OK' if result.rc == 0 else 'FAIL'}", end='\r')

def main():
    global throttle, steering
    
    # Setup MQTT client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set()
    client.on_connect = on_connect
    client.on_publish = on_publish
    
    print("Connecting to MQTT broker...")
    try:
        client.connect(BROKER, PORT, 60)
    except Exception as e:
        print(f"Connection failed: {e}")
        return
    
    client.loop_start()
    time.sleep(2)
    
    print("\nRC Car Control Ready!")
    print("Press keys to start driving...\n")
    
    try:
        while True:
            # Throttle control - FASTER ACCELERATION
            if keyboard.is_pressed('w'):
                throttle = min(100, throttle + ACCELERATION_RATE)
            elif keyboard.is_pressed('s'):
                throttle = max(-100, throttle - ACCELERATION_RATE)
            else:
                # Faster deceleration to stop
                if throttle > 0:
                    throttle = max(0, throttle - DECELERATION_RATE)
                elif throttle < 0:
                    throttle = min(0, throttle + DECELERATION_RATE)
            
            # Steering control - FASTER RESPONSE
            if keyboard.is_pressed('d'):
                steering = min(100, steering + STEERING_RATE)
            elif keyboard.is_pressed('a'):
                steering = max(-100, steering - STEERING_RATE)
            else:
                # Faster return to center
                if steering > 0:
                    steering = max(0, steering - STEERING_RETURN_RATE)
                elif steering < 0:
                    steering = min(0, steering + STEERING_RETURN_RATE)
            
            # Emergency stop
            if keyboard.is_pressed('space'):
                throttle = 0
                steering = 0
                print("\n*** EMERGENCY STOP ***", end='\r')
            
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
