from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from typing import List, Optional
import uvicorn
from deep_lake_vectordb import query_vector_search
from test_snova import summarize_text
import json
import re
app = FastAPI()
from dotenv import load_dotenv
load_dotenv()   
class QueryRequest(BaseModel):
    user_query: str

@app.post("/endpoint")
async def search_query(query: QueryRequest):
    try:
        # Query the model once
        # print(query.user_query)
        result = query_vector_search(query.user_query)
        
        # Process results
        relevant_reviews = " "
        for row in result:
            # print(row["review_context"])
            relevant_reviews = relevant_reviews + row["review_context"]
            # relevant_reviews = ''.join(relevant_reviews)
        # print(relevant_reviews)
        summary = await summarize_text(relevant_reviews, query.user_query)
        # print(summary)
        print(summary)
        # matches = re.findall(r"'''(.*?)'''", summary)
        # # summary_json = json.dumps(summary, indent=4)
        # print(matches)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)