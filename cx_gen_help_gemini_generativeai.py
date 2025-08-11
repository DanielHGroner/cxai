from cx_gen_help_utils import load_prompt_template, str_to_list, apply_prompt_substitutions, parse_ai_help_text

# Gemini import
try:
    import google.generativeai as genai
except ImportError:
    genai = None


def generate_help_gemini(source, options):
    if not genai:
        raise ImportError("google.generativeai is required for Gemini support")

    apikey = options.get("apikey") or os.getenv("GEMINI_API_KEY")
    if not apikey:
        raise ValueError("Missing Gemini API key")

    genai.configure(api_key=apikey)

    # this generates an exception (known Google issue); maybe in the future they'll have a way to get the model list
    #for m in genai.list_models():
    #    print(f"{m.name} - {m.supported_generation_methods}")

    model_name = options.get("modelName")
    temperature = options.get("temperature", 0.3)
    include_long = options.get("includeLong", True)
    language = options.get("spokenLanguage", "english")
    #prompt_path = options.get("promptFile")
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

    print('creating genai.GenerativeModel')
    model = genai.GenerativeModel(model_name)
    print('calling generate_content()')
    response = model.generate_content(prompt, generation_config={"temperature": temperature})
    print('getting response part')
    text = response.candidates[0].content.parts[0].text.strip()
    print('converting and returning result')
    return parse_ai_help_text(text)
