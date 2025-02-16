import os
from datetime import datetime
import base64
from dotenv import load_dotenv
import asyncio
import aiohttp
import json

load_dotenv()

SCREENSHOTS_DIR = "screenshots"
SAMBANOVA_API_KEY = os.getenv('SAMBANOVA_API_KEY')

if not SAMBANOVA_API_KEY:
    raise ValueError("SAMBANOVA_API_KEY not found in environment variables")

def get_latest_screenshot():
    """
    Get the path to the latest screenshot using file modification time
    """
    if not os.path.exists(SCREENSHOTS_DIR):
        raise ValueError(f"Screenshots directory '{SCREENSHOTS_DIR}' does not exist")
    
    screenshots = [f for f in os.listdir(SCREENSHOTS_DIR) if f.endswith('.png')]
    if not screenshots:
        raise ValueError("No screenshots found in directory")
    
    # Get the latest file by modification time
    latest_screenshot = max(
        screenshots,
        key=lambda x: os.path.getmtime(os.path.join(SCREENSHOTS_DIR, x))
    )
    return os.path.join(SCREENSHOTS_DIR, latest_screenshot)

async def analyze_image() -> str:
    """
    Analyze an image using SambaNova's Vision API
    """

    latest_screenshot_path = get_latest_screenshot()
    mod_time = datetime.fromtimestamp(os.path.getmtime(latest_screenshot_path))
    print(f"Found latest screenshot: {latest_screenshot_path}")
    print(f"Last modified: {mod_time}")
    
    # Read and encode the image
    with open(latest_screenshot_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    headers = {
        "Authorization": f"Bearer {SAMBANOVA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "stream": False,
        "model": "Llama-3.2-11B-Vision-Instruct",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please provide the product name in JSON format with the key 'product_name' eg : {'product_name': 'Product Name'}, do not include any other text in the response"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.sambanova.ai/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API request failed with status {response.status}: {error_text}")
                
                analysis = ""
                async for line in response.content:
                    if line:
                        try:
                            # Decode bytes to string and remove 'data: ' prefix
                            line_str = line.decode('utf-8').strip()
                            if not line_str or line_str == "data: [DONE]":  # Skip empty lines and end marker
                                continue
                                
                            # Remove the 'data: ' prefix
                            if line_str.startswith("data: "):
                                line_str = line_str[6:]  # Skip "data: "
                            
                            print(f"Processing JSON: {line_str}")  # Debug print
                            
                            data = json.loads(line_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                content = data['choices'][0]['message']['content']
                                analysis += content
                        except json.JSONDecodeError as e:
                            print(f"Skipping malformed line: {line_str}")
                            continue
                
                return analysis.strip()
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

async def main():
    try:
        # Get the latest screenshot

        
        # Analyze the image
        print("\nAnalyzing image...")
        result = await analyze_image()
        print("\nAnalysis Result:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 