from flask import Flask render_template
app=Flask(__name__)
@app.route('/',methods=['GET'])
def Assignment_2():
    return render_template('Assigment_2.html')
if __name__=='__main__':
    app.run(debug=True)
