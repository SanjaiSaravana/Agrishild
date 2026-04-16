import os
import sys
from flask import Flask, render_template, jsonify, request

# Update path to find the collectors folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from collectors.gee_api import get_satellite_analysis

app = Flask(__name__, 
            template_folder='frontend/templates', 
            static_folder='frontend/static')

@app.route('/')
def index():
    # If this still fails, double check that frontend/templates/index.html exists!
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    try:
        results = get_satellite_analysis(float(data['lat']), float(data['lon']))
        if "error" in results:
            return jsonify(results), 400
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)