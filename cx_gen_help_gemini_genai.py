import os
from cx_gen_help_utils import load_prompt_template, str_to_list, apply_prompt_substitutions, parse_ai_help_text

import warnings
# Suppress specific Pydantic shadow warnings from google-genai
warnings.filterwarnings(
    "ignore",
    message=r'.*Field name .* shadows an attribute in parent "Operation".*',
    category=UserWarning
)

# Gemini import
try:
    from google import genai
except ImportError:
    genai = None

def generate_help_gemini(source, options):
    if not genai:
        raise ImportError("google-genai (Google Gen AI SDK) is required for Gemini support")

    apikey = options.get("apikey") or os.getenv("GEMINI_API_KEY")
    if not apikey:
        raise ValueError("Missing Gemini API key")

    # this generates an exception (known Google issue); maybe in the future they'll have a way to get the model list
    #for m in genai.list_models():
    #    print(f"{m.name} - {m.supported_generation_methods}")

    model_name = options.get("modelName")
    temperature = options.get("temperature", 0.3)
    include_long = options.get("includeLong", True)
    language = options.get("spokenLanguage", "english")

    if include_long:
       prompt_path = 'prompts/gemini-short-long.txt'
    else:
        prompt_path = 'prompts/gemini-short.txt'

    template = load_prompt_template(prompt_path)
    #print('generate_help_gemini(): after load_prompt_template(); template:')
    #print(template)

    # TODO - remove code lines after code is numbered
    code_lines = str_to_list(source)

    prompt = apply_prompt_substitutions(template, code_lines, include_long, language)

    # Dryrun mode: Show prompt and return empty help
    #print('OPTIONS start:')
    #print(options)
    #print('OPTIONS end:')
    if options and options.get("dryrun", True):
        print("----- BEGIN PROMPT -----\n")
        print(prompt)
        print("\n----- END PROMPT -----")
        return {}

    print('creating genai.Client')
    # New SDK client
    client = genai.Client(api_key=apikey)

    print('calling models.generate_content()')
    response = client.models.generate_content(model=model_name, contents=prompt, config={"temperature": temperature})

    print('getting response part')
    text = response.text.strip()

    print('returning result')
    return parse_ai_help_text(text)
