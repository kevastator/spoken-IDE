import keys
import os
from openai import AzureOpenAI

# set the environmental variables
os.environ["AZURE_OPENAI_ENDPOINT"] = keys.azure_openai_endpoint
os.environ["AZURE_OPENAI_API_KEY"] = keys.azure_openai_key

# create a client instance class
client = AzureOpenAI(
    api_key=keys.azure_openai_key,  
    api_version=keys.azure_openai_api_version,
    azure_endpoint=keys.azure_openai_endpoint
    )

deployment_name = "MI_A_NAME_I_CALL_MYSELF_FA_A_LONG_LONG_WAY_TO_RUN"


