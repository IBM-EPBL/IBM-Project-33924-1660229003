from flask import Flask
app=Flask(__name__)
@app.route("/")
def home:
    return "<h1>Welcome</h1>"
if __name__=='_main_':
    app.run()    