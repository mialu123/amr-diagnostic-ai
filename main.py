from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# FastAPI app
app = FastAPI()

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Request model
class PolicyRequest(BaseModel):
    policy: str

# Demographic groups to simulate
DEMOGRAPHICS = [
    "Low-income worker",
    "Person experiencing homelessness",
    "Disabled adult",
    "LGBTQ+ individual",
    "Recent immigrant",
    "Single parent",
    "College student",
    "Senior citizen",
    "Rural resident",
    "Small business owner"
]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "landing.html",
        {"request": request}
    )

@app.get("/simulator", response_class=HTMLResponse)
async def simulator(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.post("/simulate")
async def simulate_policy(data: PolicyRequest):

    prompt = f"""
You are a public policy impact analyst.

Policy:
{data.policy}

Analyze how the following demographic groups may experience this policy:

1. Low-income worker
2. Person experiencing homelessness
3. Disabled adult
4. LGBTQ+ individual
5. Recent immigrant
6. Single parent
7. College student
8. Senior citizen
9. Rural resident
10. Small business owner

Requirements:
- Avoid stereotypes.
- Focus on realistic impacts.
- Consider employment, housing, healthcare, education, transportation, civil rights, and economic effects.
- Do not assume everyone in a demographic thinks the same way.
- Be balanced and evidence-based.

Return ONLY raw JSON.

Do not use markdown.
Do not use ```json.
Do not provide explanations before or after the JSON.
The first character must be {{
The last character must be }}

Format:

{{
  "perspectives": [
    {{
      "group": "",
      "opinion": "",
      "summary": "",
      "benefits": [],
      "concerns": []
    }}
  ]
}}
"""

    try:

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        raw_response = completion.choices[0].message.content

        print("\n========== RAW RESPONSE ==========")
        print(raw_response)
        print("==================================\n")

        # Remove markdown wrappers if the model adds them
        cleaned_response = raw_response.replace("```json", "")
        cleaned_response = cleaned_response.replace("```", "")
        cleaned_response = cleaned_response.strip()

        try:
            parsed = json.loads(cleaned_response)
            return parsed

        except json.JSONDecodeError:
            return {
                "error": "Invalid JSON returned",
                "raw_response": raw_response
            }

    except Exception as e:
        return {
            "error": str(e)
        }
@app.get("/api-status")
def api_status():
    return {
        "status": "API running"
    }
import os

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)