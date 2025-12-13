import asyncio
import websockets
import json

async def test_connection():
    uri = "ws://localhost:8000/ws"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected! Waiting for message...")
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(message)
            print("Received data!")
            print(f"Keys: {list(data.keys())}")
            print(f"Agents: {len(data.get('agents', []))}")
            print(f"Time Step: {data.get('time_step')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
