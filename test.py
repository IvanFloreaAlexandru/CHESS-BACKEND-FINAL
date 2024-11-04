import asyncio
import websockets
import time

async def test_latency(num_tests=50, your_jwt_here="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImZsb3JlYWl2YW4yMDAzQHlhaG9vLnJvIiwic3ViIjoiMTEzMjk3MjgtZTYwNC00YmRjLTg1NGQtZjMzMTM0ZTkxODE1IiwiZXhwIjoxNzI1OTYwOTAxfQ.kB7rvgPG-OL4lIf46j86g5daQQFG32_lCbLBOCcdqCQ"):
    uri = "ws://localhost:8000/ws/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImZsb3JlYWl2YW4yMDAzQHlhaG9vLnJvIiwic3ViIjoiMTEzMjk3MjgtZTYwNC00YmRjLTg1NGQtZjMzMTM0ZTkxODE1IiwiZXhwIjoxNzI1OTYwOTAxfQ.kB7rvgPG-OL4lIf46j86g5daQQFG32_lCbLBOCcdqCQ"  # Replace with your actual WebSocket URI and JWT token
    headers = {
        "Authorization": f"Bearer {your_jwt_here}"  # Add this line if your server expects the JWT in headers
    }
    latencies = []

    async with websockets.connect(uri, extra_headers=headers) as websocket:
        for i in range(num_tests):
            # Send initial message and capture time
            start_time = time.time()
            await websocket.send("ping")

            # Wait for the response
            response = await websocket.recv()
            end_time = time.time()

            # Calculate latency
            latency = end_time - start_time
            latencies.append(latency)
            print(f"Test {i+1}: Latency = {latency:.6f} seconds")

    avg_latency = sum(latencies) / len(latencies)
    print(f"\nAverage Latency over {num_tests} tests: {avg_latency:.6f} seconds")

# Run the test using asyncio.run
asyncio.run(test_latency())
