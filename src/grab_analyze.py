from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import base64
from PIL import Image
from io import BytesIO
import os
from datetime import datetime
from dotenv import load_dotenv
import aiohttp
import json
from test_snova import analyze_image
from gemini_search import process_product_analysis
load_dotenv()

app = FastAPI()
ANALYSIS_DIR = "analysis_results"
# Add CORS middleware to allow requests from the Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Get API key from environment variables
SAMBANOVA_API_KEY = os.getenv('SAMBANOVA_API_KEY')
if not SAMBANOVA_API_KEY:
    raise ValueError("SAMBANOVA_API_KEY not found in environment variables")

# Create screenshots directory if it doesn't exist
SCREENSHOTS_DIR = "screenshots"
if not os.path.exists(SCREENSHOTS_DIR):
    os.makedirs(SCREENSHOTS_DIR)

# Add this constant after other constants
ANALYSIS_DIR = "analysis_results"
if not os.path.exists(ANALYSIS_DIR):
    os.makedirs(ANALYSIS_DIR)

async def send_to_service(analysis_data):
    try:
        async with aiohttp.ClientSession() as session:
            service_url = os.getenv('SERVICE_URL', 'http://localhost:8000/api/analysis')
            async with session.post(service_url, json=analysis_data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Error sending to service: {response.status}")
                    return None
    except Exception as e:
        print(f"Error sending to service: {str(e)}")
        return None

async def save_analysis_result(analysis_data: dict) -> str:
    """Save analysis result to a JSON file"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{timestamp}.json"
        filepath = os.path.join(ANALYSIS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=4)
            
        print(f"Analysis saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error saving analysis: {str(e)}")
        return None

@app.post("/uploadimage")
async def save_screenshot(request: Request):
    try:
        # Get the JSON data from the request
        data = await request.json()
        
        # Get the base64 image data
        image_data = data['image']
        
        # Remove the data URL prefix (e.g., "data:image/png;base64,")
        if ',' in image_data:
            image_data = image_data.split(',')[1]
            
        # Decode base64 string to image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        
        # Save the image
        image.save(filepath)
        print(f"Screenshot received and saved as {filename}")
        
        # Analyze the image
        analysis = await analyze_image()
        try : 
            # breakpoint()
            import ast
            content = ast.literal_eval(analysis)
            try: 
                product_name = content['product_name']
            except Exception as e:
                print(f"Error parsing product name from analysis JSON: {str(e)}")
                assert False, "Error parsing product name from analysis"
            if product_name == "":  
                print(f"Image analysis: {analysis}")
                assert False, "Product name is empty"
        except Exception as e:
            print(f"Error parsing product name from analysis: {str(e)}")
            assert False, "Error parsing product name from analysis"
        
        print(f"Product name: {product_name}")
        
        # After analyzing the image and getting product_name
        analysis_result = {
            "status": "success",
            "filepath": filepath,
            "analysis": analysis,
            "product_name": product_name,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save analysis result to JSON
        analysis_file = await save_analysis_result(analysis_result)
        
        # Process with Gemini search
        gemini_results = process_product_analysis(product_name)
        
        # Include both results in the return
        return {
            **analysis_result,
            "analysis_file": analysis_file,
            "gemini_results": gemini_results
        }
        
    except Exception as e:
        print(f"Error saving screenshot: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
