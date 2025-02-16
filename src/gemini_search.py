from google import genai
from google.genai import types
import os
import requests
import json
from datetime import datetime

from deep_lake_vectordb import query_vector_search, create_embeddings
ANALYSIS_DIR = "analysis_results" 
class SearchAgent:  

    def __init__(self, api_key):
        """Initialize the class with the API key and configure the model."""
        self.client = genai.Client(api_key=api_key)
        self._model_string = 'gemini-2.0-flash-thinking-exp-01-21' # 'gemini-2.0-flash'
        self.history = []  # Empty list to manage search history

        # Configure the model with Google Search enabled
        self.generation_config = types.GenerateContentConfig(
            tools=[types.Tool(
                google_search=types.GoogleSearchRetrieval(
                    dynamic_retrieval_config=types.DynamicRetrievalConfig(
                        dynamic_threshold=0.6))
            )]
        )
        self.latest_response = None  # Store the latest response

    def resolve_redirect_url(self,vertex_url):
        """Follow the redirect and return the final destination URL."""
        try:
            response = requests.get(vertex_url, allow_redirects=True, timeout=5)
            return response.url  # Returns the final redirected URL
        except requests.RequestException as e:
            print(f"Error resolving URL: {vertex_url} -> {e}")
            return vertex_url  # Return the original if resolution fails
    def query(self, query):
        """Send a query to the Gemini model and return the response object."""
        response = self.client.models.generate_content(
            model =self._model_string,
            contents=query,
            config=self.generation_config
        )
        self.latest_response = response  # Store response for later retrieval
        self.update_history(query, response)  # Update history (empty for now)
        return response

    def extract_response_text(self, response):
        """Extract text from the response if available."""
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]

            if hasattr(candidate, "content") and candidate.content:
                for part in candidate.content.parts:
                    if hasattr(part, "text") and part.text:
                        return part.text  # Return first available text response
        return None  # No text found

    def extract_executable_code(self, response):
        """Extract executable code from the response if present."""
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]

            if hasattr(candidate, "content") and candidate.content:
                for part in candidate.content.parts:
                    if hasattr(part, "executable_code") and part.executable_code:
                        return part.executable_code.code  # Return the code block
        return None  # No executable code found

    def retrieve_citations(self, response, resolve_redirect=True):
        """Extract citations (source URLs) from the response."""
        citations = []
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]

            if hasattr(candidate, "grounding_metadata") and candidate.grounding_metadata:
                grounding_metadata = candidate.grounding_metadata

                if hasattr(grounding_metadata, "grounding_chunks"):
                    for chunk in grounding_metadata.grounding_chunks:
                        if hasattr(chunk, "web") and chunk.web:
                            title = chunk.web.title
                            url = chunk.web.uri

                            # Resolve redirects if flag is enabled
                            if resolve_redirect:
                                url = self.resolve_redirect_url(url)

                            citations.append(f"{title}: {url}")
        return citations  # Return list of citations

    def get_citations(self, resolve_redirect=True):
      """Return the latest retrieved citations, with optional redirect resolution."""
      if self.latest_response:
          return self.retrieve_citations(self.latest_response, resolve_redirect)
      return []

    def answer(self):
        """Return the formatted text response from the latest query."""
        if self.latest_response:
            return self.extract_response_text(self.latest_response)
        return "No response available."

    def update_history(self, query, response):
        """Placeholder function to update search history."""
        pass  # History management logic will be added later


def get_latest_analysis():
    """Get the most recent analysis result"""
    try:
        analysis_dir = "analysis_results"
        if not os.path.exists(analysis_dir):
            return None
            
        # Get the most recent analysis file
        analysis_files = [f for f in os.listdir(analysis_dir) if f.endswith('.json')]
        if not analysis_files:
            return None
            
        latest_file = max(analysis_files, key=lambda x: os.path.getctime(os.path.join(analysis_dir, x)))
        filepath = os.path.join(analysis_dir, latest_file)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
            
        return analysis_data
    except Exception as e:
        print(f"Error reading analysis: {str(e)}")
        return None


def process_product_analysis(product_name: str = None) -> dict:
    """
    Process product analysis using Gemini search
    
    Args:
        product_name (str, optional): Product name to analyze. If None, gets from latest analysis.
    
    Returns:
        dict: Results containing response and citations
    """
    try:
        API_KEY = os.getenv("GEMINI_API_KEY")
        search_bot = SearchAgent(API_KEY)

        if not product_name:
            # Get the latest analysis result
            analysis_data = get_latest_analysis()
            if not analysis_data:
                print("No analysis data found")
                return None

            product_name = analysis_data.get('product_name')
            if not product_name:
                print("No product name found in analysis")
                return None

        print(f"\nAnalyzing product: {product_name}")
        
        # Construct and send query
        query = f"{product_name} - give me details about the product and cite top youtube reviews about the product if you find it."
        search_bot.query(query)

        # Get response and citations
        response = search_bot.answer()
        citations = search_bot.get_citations()
        
        # Find first YouTube citation
        first_youtube_cite = None
        for cite in citations:
            if "youtube" in cite.lower():
                first_youtube_cite = cite
                break

        # Prepare results
        results = {
            "product_name": product_name,
            "response": response,
            "citations": citations,
            "youtube_citation": first_youtube_cite,
            "timestamp": datetime.now().isoformat()
        }

        # Save results
        save_gemini_results(results)
        
        return results

    except Exception as e:
        print(f"Error in Gemini search: {str(e)}")
        return None

def save_gemini_results(results: dict) -> str:
    """Save Gemini search results to a JSON file"""
    try:
        if not os.path.exists(ANALYSIS_DIR):
            os.makedirs(ANALYSIS_DIR)

        #add_embeddings to vector db
        print("CREATING EMBEDDINGS for PRODUCT SUMMARY....")
        create_embeddings(results['response'])
        print("EMBEDDINGS CREATED for PRODUCT SUMMARY")
        product_name = results['product_name']
        clean_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = f"gemini_{clean_name.split(' ')[0]}_{timestamp}.json"
        filepath = os.path.join(ANALYSIS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)
            
        print(f"Gemini results saved to: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error saving Gemini results: {str(e)}")
        return None

if __name__ == "__main__":
    results = process_product_analysis()
    if results:
        print("\nResponse:")
        print(results['response'])
        print("\nCitations:")
        for cite in results['citations']:
            print(cite)
        if results['youtube_citation']:
            print(f"\nFirst YouTube Citation: {results['youtube_citation']}")

