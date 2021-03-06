import pandas as pd
from flask import Flask, jsonify, make_response, request, abort
import pandas as pd

from vodkas.simple_db import SimpleDB

DEFAULT_APP_PORT = 8745
DB = SimpleDB('/home/matteo/Projects/vodkas/vodkas/devel/server_stuff/logs.db')
app = Flask(__name__)


@app.route('/greet', methods=['POST'])
def receive_greeting():
    """Receive greeting from the sender."""
    if request.data:
        greeting = request.get_json()
        return jsonify(len(DB))

@app.route('/log', methods=['POST'])
def receive_log():
    """Receive logs.
    
    Returns:
        boolean: was all successfull.
    """
    if request.data:
        try:
            log = request.get_json()
            log['processing_computer_IP'] = str(request.remote_addr)
            row = pd.DataFrame()
            row = row.append(log, ignore_index=True)
            print(row)
            DB.append(row)
            return jsonify(True)
        except Exception as e:
            print(e)
    return jsonify(False)

@app.route('/df', methods=['POST'])
def df():
    """Send the entire DB back."""
    return DB.df().to_json()



if __name__ == '__main__':
    port = DEFAULT_APP_PORT
    app.run(debug=False,
            host='0.0.0.0',
            port=port,
            threaded=False)
