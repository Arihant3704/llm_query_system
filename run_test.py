import os
import json
import httpx
from dotenv import load_dotenv

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_query_system.main import app

load_dotenv()

API_KEY = os.environ.get("API_KEY")

async def main():
    document_path = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
    questions = [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?",
        "What is the waiting period for cataract surgery?",
        "Are the medical expenses for an organ donor covered under this policy?",
        "What is the No Claim Discount (NCD) offered in this policy?",
        "Is there a benefit for preventive health check-ups?",
        "How does the policy define a 'Hospital'?",
        "What is the extent of coverage for AYUSH treatments?",
        "Are there any sub-limits on room rent and ICU charges for Plan A?"
    ]

    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "documents": document_path,
        "questions": questions
    }

    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/hackrx/run", json=data, headers=headers, timeout=120)

    output_dir = "/home/arihant/llm_query_system/output"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "test_results.json")

    with open(output_file, 'w') as f:
        json.dump(response.json(), f, indent=4)

    print(f"Test results saved to {output_file}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())