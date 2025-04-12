from openai import AzureOpenAI

# Store your API key in an environment variable for security (best practice)
# For now, setting it directly in the script, but consider using environment variables
api_key = "3L2W6niZ2aTcZWiobBG5d54g3M3xTvbbUWqLjuhajbyDYIpJ6xRGJQQJ99BDACYeBjFXJ3w3AAABACOGzqpD"

# Create an Azure OpenAI client
client = AzureOpenAI(
    api_key=api_key,
    api_version="2025-01-01-preview",  # GPT-4o is under this version
    azure_endpoint="https://swisshacks-3plus1.openai.azure.com"
)

# Make the API call
response = client.chat.completions.create(
    model="gpt-4o",  # Use the deployment name you chose
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."}
    ]
)

print(response.choices[0].message.content)