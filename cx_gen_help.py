import argparse
from dotenv import load_dotenv
from cx_gen_help_utils import str_to_list, parse_ai_help_text
from cx_gen_help_gemini_genai import generate_help_gemini


# --- Defaults and Configuration ---
DEFAULTS = {
    "gemini": {
        "modelName": "gemini-2.5-flash-lite",
        "temperature": 0.3,
        "includeLong": True,
        "spokenLanguage": "english",
        "promptFile": "prompts/gemini-short-long.txt"
    },
    "dummy": {
        "includeLong": True,
        "spokenLanguage": "english"
    }
}

# --- Providers ---
def generate_help_dummy(source, options):
    include_long = options.get("includeLong", True)
    code_lines = str_to_list(source)
    help_lines = []
    line0help = "000|Dummy Program Description" + ("|This is a dummy overall help for program" if include_long else "") + ';';
    for i, line in enumerate(code_lines):
        lineno = str(i+1).zfill(3)
        if include_long:
            help_lines.append(f"{lineno}|Dummy short help line {lineno}|This is dummy long help for line {lineno};")
        else:
            help_lines.append(f"{lineno}|Dummy short help line {lineno};")
    return parse_ai_help_text("\n".join([line0help] + help_lines))


# --- Main Dispatcher ---
def cx_gen_help(source: str, options: dict) -> dict:
    provider = options.get("apiProvider", "gemini").lower()
    print("🔍 Using provider:", provider)
    print("📄 promptFile in DEFAULTS:", DEFAULTS.get(provider, {}).get("promptFile"))

    merged_opts = {
       **DEFAULTS.get(provider, {}),
       **{k: v for k, v in options.items() if v is not None}
    }
    print("📦 Merged options:", merged_opts)

    if provider == "dummy":
        return generate_help_dummy(source, merged_opts)
    elif provider == "gemini":
        return generate_help_gemini(source, merged_opts)
    else:
        raise ValueError(f"Unsupported provider: {provider}")

# --- CLI ---
if __name__ == "__main__":
    load_dotenv("env_vars.env")

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Python source file")
    parser.add_argument("--dryrun", type=str2bool, default=True, help="Enable/disable dry run mode (default: true)")
    parser.add_argument("--provider", default="gemini", help="API provider (gemini or dummy)")
    parser.add_argument("--apikey", default=None, help="API key (optional if set in .env)")
    parser.add_argument("--modelName", default=None, help="Model name override for Gemini")
    parser.add_argument("--temperature", type=float, default=None, help="Sampling temperature")
    parser.add_argument("--includeLong", type=str2bool, default=True, help="Include long help")
    parser.add_argument("--language", default="english", help="Spoken language for help text")
    parser.add_argument("--promptFile", default=None, help="Prompt template file")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    with open(args.filename, encoding="utf-8") as f:
        code = f.read()

    opts = {
        "apiProvider": args.provider,
        "apikey": args.apikey,
        "modelName": args.modelName,
        "temperature": args.temperature,
        "includeLong": args.includeLong,
        "spokenLanguage": args.language,
        "promptFile": args.promptFile,
        "dryrun": args.dryrun
    }

    if args.debug:
        print("Merged options:", {k: v for k, v in opts.items() if v is not None})

    help_result = cx_gen_help(code, opts)
    for k, v in help_result.items():
        print(f"{k}|{v['short']}|{v['long']};")
