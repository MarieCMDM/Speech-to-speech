from src.server import app
from dotenv import load_dotenv
import os 

load_dotenv()
# cert_path = os.getenv('SSL_CERT_PATH')
# key_path = os.getenv('SSL_KEY_PATH')

if __name__ == '__main__':
    # context = (cert_path, key_path)
    context = 'adhoc'
    app.run(host='0.0.0.0', port=5100, debug=True, ssl_context=context)