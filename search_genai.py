from google import genai
from google.genai import types
import os

class SearchAgent:
    history = []  # Empty list to manage search history

    def __init__(self, api_key):
        """Initialize the class with the API key and configure the model."""
        self.client = genai.Client(api_key=api_key)

        # Configure the model with Google Search enabled
        self.generation_config = types.GenerateContentConfig(
            tools=[types.Tool(
                google_search=types.GoogleSearchRetrieval(
                    dynamic_retrieval_config=types.DynamicRetrievalConfig(
                        dynamic_threshold=0.6))
            )]
        )
        self.latest_response = None  # Store the latest response

    def query_model(self, query):
        """Send a query to the Gemini model and return the response object."""
        response = self.client.models.generate_content(
            model='gemini-2.0-flash',
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

    def retrieve_citations(self, response):
        """Extract citations (source URLs) from the response."""
        citations = []
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]

            if hasattr(candidate, "grounding_metadata") and candidate.grounding_metadata:
                grounding_metadata = candidate.grounding_metadata
                
                if hasattr(grounding_metadata, "grounding_chunks"):
                    for chunk in grounding_metadata.grounding_chunks:
                        if hasattr(chunk, "web") and chunk.web:
                            citations.append(f"{chunk.web.title}: {chunk.web.uri}")
        return citations  # Return list of citations

    def get_citations(self):
        """Return the latest retrieved citations."""
        if self.latest_response:
            return self.retrieve_citations(self.latest_response)
        return []

    def answer(self):
        """Return the formatted text response from the latest query."""
        if self.latest_response:
            return self.extract_response_text(self.latest_response)
        return "No response available."

    def update_history(self, query, response):
        """Placeholder function to update search history."""
        pass  # History management logic will be added later


# === Main Loop ===
if __name__ == "__main__":
    
    API_KEY = os.getenv("GEMINI_API_KEY")
    
    search_bot = SearchAgent(API_KEY)  # Create an instance of the class

    query = "What is the latest Apple product rumored?"
    search_bot.query_model(query)

    # Answer
    print("\nResponse:")
    print(search_bot.answer())

    # Citations
    citations = search_bot.get_citations()
    print("\nCitations:")
    for cite in citations:
        print(cite)
