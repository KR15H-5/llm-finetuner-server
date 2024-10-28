from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware
from gradientai import Gradient
from supabase import create_client, Client
import os
import uvicorn
import json
import logging
from dotenv import load_dotenv

load_dotenv()
# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Gradientai setup
os.environ['GRADIENT_ACCESS_TOKEN'] = os.getenv("GRADIENT_ACCESS_TOKEN")
os.environ['GRADIENT_WORKSPACE_ID'] = os.getenv("GRADIENT_WORKSPACE_ID")
MODEL_ADAPTERS_FILE = 'model_adapters.json'

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

origins = [
    "http://127.0.0.1:5500",  # testing frontend origin
    "http://localhost:5500",# testing frontend origin
    "https://essay-llm-finetuner.vercel.app",   # testing frontend origin
    "http://essay-llm-finetuner.vercel.app",# testing frontend origin
    "http://127.0.0.1:8000",# testing frontend origin
    "https://finetune.krishshroff.com" # Main frontend origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Number(BaseModel):
    value: int


class GenerateRequest(BaseModel):
    user_id: EmailStr
    prompt: str

class UserEmail(BaseModel):
    user_id: EmailStr



def fetch_user_data(user_id):
    try:
        response = supabase.table("essay-data").select("*").eq("userid", user_id).execute()
        # if response.status_code != 200:
        #     raise HTTPException(status_code=response.status_code, detail=response.json().get('message', 'Error fetching data from Supabase'))
        return response.data
    except Exception as e:
        logger.error(f"Error fetching data from Supabase: {e}")
        raise HTTPException(status_code=500, detail="Error fetching data from Supabase")


model_adapters = {}
def save_model_adapters():
    try:
        with open(MODEL_ADAPTERS_FILE, 'w') as f:
            json.dump(model_adapters, f)
    except Exception as e:
        logger.error(f"Error saving model adapters: {e}")
        raise HTTPException(status_code=500, detail="Error fetching data from Supabase")


# @app.post("/fine-tune")
# async def process_number(number: Number):
#     print(f"Received number: {number.value}")
#     user_data = fetch_user_data(number.value)
#     print(user_data)
#     # if not user_data::
#     #     raise HTTPException(status_code=404, detail="No data found for the given user ID")
#     return {"received_number": number.value}
@app.post("/fine-tune")
async def fine_tune(user_email: UserEmail):
    try:
        user_data = fetch_user_data(user_email.user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="No data found for the given user ID")

        with Gradient() as gradient:
            base_model = gradient.get_base_model(base_model_slug="nous-hermes2")
            new_model_adapter = base_model.create_model_adapter(name=f"model_for_{user_email.user_id}")
            adapter_id = new_model_adapter.id
            model_adapters[f"model_for_{user_email.user_id}"] = adapter_id

            save_model_adapters()

            sample_query = "### Instruction: Write an 300 word essay about AI impact on the world? \n\n### Response:"
            # print(f"Asking: {sample_query}")

            # # before fine-tuning
            # completion = new_model_adapter.complete(query=sample_query, max_generated_token_count=100).generated_output
            # print(f"Generated (before fine-tune): {completion}")

            samples = [{"inputs": f"### Instruction: {record['prompt']} \n\n### Response: {record['content']}"} for record in user_data]
            num_epochs = 3
            for epoch in range(num_epochs):
                logger.info(f"Fine-tuning the model, iteration {epoch + 1}")
                new_model_adapter.fine_tune(samples=samples)

            # completion_after = new_model_adapter.complete(query=sample_query, max_generated_token_count=100).generated_output
            # print(f"Generated (after fine-tune): {completion_after}")
           
            return {
                "message": "Model fine-tuned successfully with model number " + str(user_email.user_id),
            }

    except Exception as e:
        logger.error(f"Error during fine-tuning: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@app.post("/generate")
async def generate(request: GenerateRequest):
    try:
        model_name = f"model_for_{request.user_id}"
        logger.info(f"Looking for model adapter with name: {model_name}")
        
        with Gradient() as gradient:
            model_name = f"model_for_{request.user_id}"
            logger.info(f"Looking for model adapter with name: {model_name}")

            # Load model adapters dict from the file
            if os.path.exists(MODEL_ADAPTERS_FILE):
                with open(MODEL_ADAPTERS_FILE, 'r') as f:
                    model_adapters = json.load(f)
            else:
                raise HTTPException(status_code=404, detail="Model adapters file not found")

            # Retrieves the adapter ID
            model_adapter_id = model_adapters.get(model_name)
            
            # Access the model adapter using the found ID
            model_adapter = gradient.get_model_adapter(model_adapter_id=model_adapter_id)
            completion = model_adapter.complete(query=request.prompt, max_generated_token_count=500).generated_output

        return {"generated_text": completion}

    except Exception as e:
        logger.error(f"Error during text generation: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/view-model-adapters")
async def view_model_adapters():
    try:
        if os.path.exists(MODEL_ADAPTERS_FILE):
            with open(MODEL_ADAPTERS_FILE, 'r') as f:
                model_adapters = json.load(f)
            return model_adapters
        else:
            raise HTTPException(status_code=404, detail="Model adapters file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")