from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings 

from config import settings

# Azure OpenAI configuration
AZURE_OPENAI_ENDPOINT = settings.AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_API_KEY = settings.AZURE_OPENAI_API_KEY
AZURE_OPENAI_API_VERSION = settings.AZURE_OPENAI_API_VERSION
AZURE_OPENAI_DEPLOYMENT = settings.AZURE_OPENAI_DEPLOYMENT

# Azure OpenAI Embeddings configuration
AZURE_OPENAI_EMBED_API_ENDPOINT = settings.AZURE_OPENAI_EMBED_API_ENDPOINT
AZURE_OPENAI_EMBED_API_KEY = settings.AZURE_OPENAI_EMBED_API_KEY
AZURE_OPENAI_EMBED_MODEL = settings.AZURE_OPENAI_EMBED_MODEL
AZURE_OPENAI_EMBED_VERSION = settings.AZURE_OPENAI_EMBED_VERSION

# Initialize Azure OpenAI model
model = AzureChatOpenAI(
    azure_deployment=AZURE_OPENAI_DEPLOYMENT,
    openai_api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
)

# Initialize Azure OpenAI Embeddings
embedding_model = AzureOpenAIEmbeddings(
    deployment=AZURE_OPENAI_EMBED_MODEL,
    openai_api_version=AZURE_OPENAI_EMBED_VERSION,
    azure_endpoint=AZURE_OPENAI_EMBED_API_ENDPOINT,
    api_key=AZURE_OPENAI_EMBED_API_KEY,
)