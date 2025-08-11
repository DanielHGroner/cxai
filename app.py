from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import traceback
import cx_gen_help

load_dotenv("env_vars.env")

app = Flask(__name__)
CORS(app)  # allow cross-origin

#@app.route("/")
#def serve_test_page():
#    return send_from_directory(".", "cx_help_test.html")

@app.route("/")
def serve_test_page():
    return render_template("cx_help_test.html")
#    return send_from_directory(".", "cx_help_test.html")

@app.route("/aihelp", methods=["POST"])
def ai_help():
    print('Entering ai_help() ***', flush=True)
    try:
        data = request.json
        source = data.get("source", "")
        options = data.get("options", {})

        if not source:
            raise ValueError("Missing source code")

        result = cx_gen_help.cx_gen_help(source, options)

        print('ai_help(): Call to cx_gen_help() OK; Returing results', flush=True)

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
        print('ai_help(): Exception')
        traceback.print_exc()
        return jsonify({
            "metadata": {
                "success": False,
                "error": str(e)
            },
            "data": {}
        }), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
