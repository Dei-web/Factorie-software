import os

from dotenv import load_dotenv
from strands.models.openai import OpenAIModel

load_dotenv()

model = OpenAIModel(
    client_args={
        "api_key": os.environ["NVIDIA_API_KEY"],
        "base_url": "https://integrate.api.nvidia.com/v1",
    },
    model_id="nvidia/nemotron-3.5-super-vl-120b-a12b",
    params={
        "temperature": 0.3,
        "max_tokens": 16384,
        "reasoning_effort": "none",
    },
)
