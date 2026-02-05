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
CONSTANT_SPEED = 40         # SLOWER SPEED (was 60, now 40 = slower)
                            # Try: 30 = very slow, 40 = slow, 50 = medium
CONSTANT_STEERING = 50      # GENTLER STEERING (was 70, now 50)
                            # Try: 40 = wide turns, 50 = normal, 60 = sharp
UPDATE_RATE = 0.02          # How often to send commands (50 times per second)
# =========================================

# Control variables
throttle = 0
steering = 0

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to MQTT Broker! Return code: {reason_code}")
    if reason_code == 0:
        print("Successfully connected!")
        print("\n" + "="*60)
        print("         RC CAR CONTROLS - SLOW & STEADY MODE")
        print("="*60)
        print("W        - Forward (hold key = keeps moving)")
        print("S        - Backward (hold key = keeps moving)")
        print("A        - Left Turn")
        print("D        - Right Turn")
        print("SPACE    - Emergency Stop")
        print("ESC      - Quit")
        print("="*60)
        print(f"\nSpeed Settings:")
        print(f"  Movement Speed: {CONSTANT_SPEED}% (slower & controlled)")
        print(f"  Steering Power: {CONSTANT_STEERING}%")
        print(f"  NO TIME LIMIT - moves as long as you hold the key!")
        print("="*60 + "\n")
    else:
        print(f"Failed to connect, return code {reason_code}")

def send_command(client):
    message = f"{throttle},{steering}"
    result = client.publish(TOPIC, message, qos=1)
    
    # Display status with directional indicator
    direction = ""
    if throttle > 0 and steering == 0:
        direction = "↑ FORWARD (SLOW)"
    elif throttle < 0 and steering == 0:
        direction = "↓ BACKWARD (SLOW)"
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
    
    print(f"Throttle: {throttle:4}% | Steering: {steering:4}% | {direction:25}", end='\r')

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
    
    print("\nRC Car Ready!")
    print("Press and HOLD keys to move continuously...\n")
    
    try:
        while True:
            # CONTINUOUS MOVEMENT - No time limit!
            # Bot moves as long as you hold the key down
            
            # Throttle control
            if keyboard.is_pressed('w'):
                throttle = CONSTANT_SPEED      # Forward at slow constant speed
            elif keyboard.is_pressed('s'):
                throttle = -CONSTANT_SPEED     # Backward at slow constant speed
            else:
                throttle = 0                    # Stop immediately when released
            
            # Steering control
            if keyboard.is_pressed('d'):
                steering = CONSTANT_STEERING    # Turn right
            elif keyboard.is_pressed('a'):
                steering = -CONSTANT_STEERING   # Turn left
            else:
                steering = 0                    # Center when released
            
            # Emergency stop
            if keyboard.is_pressed('space'):
                throttle = 0
                steering = 0
                print("\n*** EMERGENCY STOP ***" + " "*30, end='\r')
            
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
    print("\n" + "="*60)
    print("  ESP32 RC Car Controller - Slow & Continuous Mode")
    print("="*60)
    print("\nIMPORTANT NOTES:")
    print("  • Hold 'W' for 1 second  = Bot moves forward for 1 second")
    print("  • Hold 'W' for 10 seconds = Bot moves forward for 10 seconds")
    print("  • Hold 'W' for 1 minute  = Bot moves forward for 1 minute")
    print("  • There is NO automatic time limit!")
    print("  • Release key = Bot stops immediately")
    print("="*60 + "\n")
    
    main()
