import os
import traceback
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import cx_gen_help

app = Flask(__name__)
CORS(app)  # allow cross-origin

# set up logging
log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
log_level_num = getattr(logging, log_level, logging.INFO)
logger = logging.getLogger()
logger.setLevel(log_level_num)
if os.environ.get('FLASK_ENV') == 'development':
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
else:
    #log_file_path = os.path.join(os.path.expanduser('~'), 'cxai_app.log')
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(base_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, 'cxai_app.log')

    file_handler = RotatingFileHandler(log_file_path, maxBytes=1024 * 1024, backupCount=3)
    #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

#logging.basicConfig(level=log_level_num, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#app.logger.setLevel(log_level_num)
#app.logger.info(f"Logging level set to: {log_level}")

#@app.route("/")
#def serve_test_page():
#    return send_from_directory(".", "cx_help_test.html")

@app.route("/")
def serve_test_page():
    return render_template("cx_help_test.html")
#    return send_from_directory(".", "cx_help_test.html")

@app.route("/aihelp", methods=["POST"])
def ai_help():
    #print('Entering ai_help() ***', flush=True)
    app.logger.info('Entering ai_help() ***')
    try:
        data = request.json
        source = data.get("source", "")
        options = data.get("options", {})

        if not source:
            raise ValueError("Missing source code")

        result = cx_gen_help.cx_gen_help(source, options)

        #print('ai_help(): Call to cx_gen_help() OK; Returing results', flush=True)
        app.logger.info('ai_help(): Call to cx_gen_help() OK; Returing results')

        return jsonify({
            "metadata": {
                "success": True,
                "provider": options.get("apiProvider", "unknown"),
                "model": options.get("modelName", ""),
                "language": options.get("spokenLanguage", "english")
            },
            "data": result
        })

    except Exception as e:
        #print('ai_help(): Exception')
        #traceback.print_exc()
        app.logger.exception('ai_help(): Exception')
        return jsonify({
            "metadata": {
                "success": False,
                "error": str(e)
            },
            "data": {}
        }), 500

if __name__ == "__main__":
    load_dotenv("env_vars.env")
    app.run(debug=True, port=5001)
