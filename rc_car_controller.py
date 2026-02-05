import paho.mqtt.client as mqtt
import keyboard
import time

# MQTT Configuration
BROKER = "1887637a30c2432683efd36d80813f78.s1.eu.hivemq.cloud"
PORT = 8883  # FIXED: Changed from 8884 to match ESP32
USERNAME = "titaniumrobotics"
PASSWORD = "Sapt090059#"
TOPIC = "rccar/control"

# Control variables
throttle = 0
steering = 0

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to MQTT Broker! Return code: {reason_code}")  # FIXED: Changed rc to reason_code
    if reason_code == 0:  # FIXED: Changed rc to reason_code
        print("Successfully connected!")
        print("\nControls:")
        print("W/S - Forward/Backward")
        print("A/D - Left/Right")
        print("SPACE - Stop")
        print("ESC - Quit")
    else:
        print(f"Failed to connect, return code {reason_code}")

def on_publish(client, userdata, mid, reason_code, properties):
    # Callback to confirm message was sent
    pass

def send_command(client):
    message = f"{throttle},{steering}"
    result = client.publish(TOPIC, message, qos=1)  # ADDED: QoS 1 for reliability
    print(f"Sent: Throttle={throttle}%, Steering={steering}% | Status: {result.rc}", end='\r')

def main():
    global throttle, steering
    
    # Setup MQTT client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set()  # Enable SSL/TLS
    client.on_connect = on_connect
    client.on_publish = on_publish
    
    print("Connecting to MQTT broker...")
    try:
        client.connect(BROKER, PORT, 60)
    except Exception as e:
        print(f"Connection failed: {e}")
        return
    
    client.loop_start()
    
    time.sleep(2)  # Wait for connection
    
    print("\nRC Car Control Ready!")
    print("Make sure your ESP32 is connected and subscribed!")
    
    try:
        while True:
            # Throttle control
            if keyboard.is_pressed('w'):
                throttle = min(100, throttle + 5)
            elif keyboard.is_pressed('s'):
                throttle = max(-100, throttle - 5)
            else:
                # Gradual deceleration
                if throttle > 0:
                    throttle = max(0, throttle - 3)
                elif throttle < 0:
                    throttle = min(0, throttle + 3)
            
            # Steering control
            if keyboard.is_pressed('d'):
                steering = min(100, steering + 5)
            elif keyboard.is_pressed('a'):
                steering = max(-100, steering - 5)
            else:
                # Return to center
                if steering > 0:
                    steering = max(0, steering - 5)
                elif steering < 0:
                    steering = min(0, steering + 5)
            
            # Emergency stop
            if keyboard.is_pressed('space'):
                throttle = 0
                steering = 0
            
            # Quit
            if keyboard.is_pressed('esc'):
                throttle = 0
                steering = 0
                send_command(client)
                print("\n\nStopping car and exiting...")
                break
            
            send_command(client)
            time.sleep(0.05)  # 20Hz update rate
            
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

if __name__ == "__main__":
    main()
