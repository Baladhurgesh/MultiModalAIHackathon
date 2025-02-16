from typing import Dict, List, Optional, Union
import google.generativeai as genai
from dotenv import load_dotenv
import os
from yt import YouTubeProcessor

# Load environment variables
load_dotenv()

class YouTubeAnalyzer:
    def __init__(self, url: str):
        """
        Initialize the YouTube analyzer with a video URL
        
        Args:
            url (str): YouTube video URL
        
        Example:
            >>> analyzer = YouTubeAnalyzer("https://www.youtube.com/watch?v=3f8dv72Ex6U")
        """
        self.processor = YouTubeProcessor()
        self.video_id = self.processor.extract_video_id(url)
        if not self.video_id:
            raise ValueError("Invalid YouTube URL")
        
        # Cache video info and transcript
        self.video_info = self.processor.get_video_info(self.video_id)
        self.transcript = self.processor.get_transcript(self.video_id)

    def get_video_details(self) -> Dict:
        """
        Get basic video information
        
        Returns:
            Dict containing video title, channel, views, likes
            
        Example:
            >>> details = analyzer.get_video_details()
            >>> print(details['title'])
        """
        return self.video_info

    def get_summary(self) -> str:
        """
        Get a summary of the video content
        
        Returns:
            str: Summary of the video
            
        Example:
            >>> summary = analyzer.get_summary()
            >>> print(summary)
        """
        return self.processor.get_summary(self.video_id)

    def search(self, query: str) -> List[Dict]:
        """
        Search the video transcript for relevant segments
        
        Args:
            query (str): Search query (e.g., "talk about coffee beans")
            
        Returns:
            List of dictionaries containing:
                - timestamp: "[MM:SS]" format
                - text: Relevant transcript text
                - hyperlink: Direct YouTube URL with timestamp
                - answer: Relevant segment text
                
        Example:
            >>> results = analyzer.search("coffee grinding technique")
            >>> for result in results:
            >>>     print(f"Link: {result['hyperlink']}")
            >>>     print(f"Answer: {result['answer']}")
        """
        results = self.processor.search_transcript(self.video_id, query)
        if not results:
            return []
        
        # Reformat results to match API structure
        formatted_results = []
        for result in results:
            formatted_results.append({
                'timestamp': result['timestamp'],
                'hyperlink': result['url'],
                'answer': result['text']
            })
        
        return formatted_results

def main():
    """Example usage of the YouTubeAnalyzer"""
    
    # Example 1: Basic initialization and video info
    print("\nExample 1: Initialize and get video info")
    print("-" * 50)
    try:
        analyzer = YouTubeAnalyzer("https://www.youtube.com/watch?v=3f8dv72Ex6U")
        details = analyzer.get_video_details()
        print(f"Video Title: {details['title']}")
        print(f"Channel: {details['channel']}")
    except Exception as e:
        print(f"Error: {str(e)}")

    # Example 2: Get video summary
    print("\nExample 2: Get video summary")
    print("-" * 50)
    try:
        summary = analyzer.get_summary()
        print(f"Summary: {summary[:200]}...")  # Print first 200 chars
    except Exception as e:
        print(f"Error: {str(e)}")

    # Example 3: Search for specific content
    print("\nExample 3: Search transcript")
    print("-" * 50)
    try:
        results = analyzer.search("tell me about static build up")
        for result in results:
            print(f"\nTimestamp: {result['timestamp']}")
            print(f"Answer: {result['answer']}")
            print(f"Link: {result['hyperlink']}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
