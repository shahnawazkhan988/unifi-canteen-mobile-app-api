#from flask import Flask
#from unifimensa.main import main
from unifi import create_app

app = create_app()

if __name__ == "__main__":
    #app = create_app()
    #port = int(os.environ.get("PORT", 5000))
    #app.run(host='0.0.0.0', port=port)
    app.config["APPLICATION_ROOT"] = "/api/v1"
    app.run()