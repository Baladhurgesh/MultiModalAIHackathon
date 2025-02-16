from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import os
from dotenv import load_dotenv
import re
import google.generativeai as genai
from typing import List, Dict, Optional

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

class YouTubeProcessor:
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.transcript_cache = None
        self.video_info_cache = None

    def extract_video_id(self, url: str) -> str:
        """Extract video ID from various forms of YouTube URLs"""
        try:
            patterns = [
                r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
                r'(?:embed\/)([0-9A-Za-z_-]{11})',
                r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            return None
        except Exception as e:
            print(f"Error extracting video ID: {str(e)}")
            return None

    def get_video_info(self, video_id: str) -> dict:
        """Retrieve video information using YouTube API"""
        try:
            if self.video_info_cache:
                return self.video_info_cache

            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()

            if not response['items']:
                return None

            video_data = response['items'][0]
            self.video_info_cache = {
                'title': video_data['snippet']['title'],
                'description': video_data['snippet']['description'],
                'channel': video_data['snippet']['channelTitle'],
                'published_at': video_data['snippet']['publishedAt'],
                'view_count': video_data['statistics']['viewCount'],
                'like_count': video_data['statistics'].get('likeCount', 'N/A'),
                'duration': video_data['contentDetails']['duration']
            }
            return self.video_info_cache
        except Exception as e:
            print(f"Error getting video info: {str(e)}")
            return None

    def get_transcript(self, video_id: str) -> List[Dict]:
        """Retrieve video transcript with timestamps"""
        try:
            if self.transcript_cache:
                return self.transcript_cache

            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Format each transcript entry with timestamp
            formatted_transcript = []
            for entry in transcript_list:
                # Convert duration to minutes and seconds
                start_seconds = int(entry['start'])
                minutes = start_seconds // 60
                seconds = start_seconds % 60
                
                # Format timestamp and text
                timestamp = f"[{minutes:02d}:{seconds:02d}]"
                formatted_entry = {
                    'timestamp': timestamp,
                    'text': entry['text'],
                    'start': entry['start'],
                    'duration': entry['duration']
                }
                formatted_transcript.append(formatted_entry)
            
            self.transcript_cache = formatted_transcript
            return formatted_transcript
        except Exception as e:
            print(f"Error getting transcript: {str(e)}")
            return None

    def get_summary(self, video_id: str) -> str:
        """Generate a summary of the video using Gemini"""
        try:
            transcript = self.get_transcript(video_id)
            if not transcript:
                return None

            # Combine all transcript text
            full_text = " ".join([entry['text'] for entry in transcript])
            
            # Generate summary using Gemini
            prompt = f"Please provide a concise summary of this video transcript:\n\n{full_text}"
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return None

    def search_transcript(self, video_id: str, query: str) -> List[Dict]:
        """Search transcript for relevant segments using Gemini"""
        try:
            transcript = self.get_transcript(video_id)
            if not transcript:
                return None

            # Create context for Gemini
            context = "This is a YouTube video transcript with timestamps. "
            context += "Find the most relevant segments that answer this question. Doesnt have to be exact but make sure it's relevant in semantic meaning and context: "
            context += f"'{query}'\n\n"
            
            # Add transcript segments
            for entry in transcript:
                context += f"{entry['timestamp']}: {entry['text']}\n"

            prompt = context + "\nPlease identify and return the most relevant timestamps and their text that answer the query. Format your response as: [MM:SS] Text content"
            
            response = model.generate_content(prompt)
            
            # Process and format the response
            relevant_segments = []
            for line in response.text.split('\n'):
                if '[' in line and ']' in line:  # Check if line contains timestamp
                    # Find matching original transcript entry for additional metadata
                    timestamp = line[line.find('['): line.find(']')+1]
                    for entry in transcript:
                        if entry['timestamp'] == timestamp:
                            # Create YouTube timestamp URL
                            time_seconds = int(entry['start'])
                            youtube_url = f"https://youtube.com/watch?v={video_id}&t={time_seconds}"
                            
                            relevant_segments.append({
                                'timestamp': timestamp,
                                'text': line[line.find(']')+1:].strip(),
                                'start': entry['start'],
                                'duration': entry['duration'],
                                'url': youtube_url
                            })
                            break

            return relevant_segments
        except Exception as e:
            print(f"Error searching transcript: {str(e)}")
            return None

def main():
    # Initialize the processor
    yt = YouTubeProcessor()
    
    # Get video URL from user
    # video_url = input("Please enter the YouTube video URL: ")
    video_url = "https://www.youtube.com/watch?v=3f8dv72Ex6U&ab_channel=JamesHoffmann"
    
    # Extract video ID
    video_id = yt.extract_video_id(video_url)
    if not video_id:
        print("Invalid YouTube URL")
        return
    
    # Get video information
    print("\nRetrieving video information...")
    video_info = yt.get_video_info(video_id)
    if video_info:
        print("\nVideo Information:")
        print(f"Title: {video_info['title']}")
        print(f"Channel: {video_info['channel']}")
        print(f"Views: {video_info['view_count']}")
        print(f"Likes: {video_info['like_count']}")
    
    # Get and display summary
    print("\nGenerating video summary...")
    summary = yt.get_summary(video_id)
    if summary:
        print("\nVideo Summary:")
        print(summary)

    # Interactive search loop
    while True:
        query = input("\nEnter search query (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break

        print("\nSearching transcript...")
        results = yt.search_transcript(video_id, query)
        if results:
            print("\nRelevant segments:")
            for entry in results:
                print(f"{entry['timestamp']} {entry['text']}")
                print(f"🔗 Watch this segment: {entry['url']}")
                print("-" * 50)
        else:
            print("No relevant segments found")

if __name__ == "__main__":
    main()
