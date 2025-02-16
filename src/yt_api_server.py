from flask import Flask, request, jsonify
from yt_api import YouTubeProcessor

app = Flask(__name__)

# Hardcoded video URL from your yt_api.py
VIDEO_URL = "https://www.youtube.com/watch?v=3f8dv72Ex6U&ab_channel=JamesHoffmann"

@app.route('/api/video/links', methods=['POST'])
def get_video_links():
    try:
        data = request.get_json()
        
        # Check if query is present
        if not data or 'query' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing required parameter: query"
            }), 400

        # Initialize YouTubeProcessor only when needed
        yt_processor = YouTubeProcessor()
            
        # Extract video ID from hardcoded URL
        video_id = yt_processor.extract_video_id(VIDEO_URL)
        if not video_id:
            return jsonify({
                "status": "error",
                "message": "Invalid YouTube URL"
            }), 400

        # Search transcript
        results = yt_processor.search_transcript(video_id, data['query'])
        if not results:
            return jsonify({
                "status": "error",
                "message": "No results found"
            }), 404

        # Return only timestamps and URLs
        return jsonify({
            "status": "success",
            "results": [{
                "timestamp": segment['timestamp'],
                "url": segment['url']
            } for segment in results]
        })

    except Exception as e:
        print(f"Error: {str(e)}")  # Add this for debugging
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)