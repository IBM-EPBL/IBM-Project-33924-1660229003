from flask import Flask,request,json

app=Flask(__name__)
states={"1":"Andhra Pradesh","2":"Tamil Nadu","3":"Telangana","4":"kerala","5":"punjab","6":"uttar pradesh","7":"Andaman"}
@app.route('/data',methods=['GET','POST'])
def api():
    if request.method=='GET':
        return states
    if request.method=='POST':
        data=request.json
        states.update(data)
        return 'Hey your data got inserted'
    @app.route("/data/<id>",methods=['PUT'])
    def update(id):
        data=request.form['item']
        states[str(id)]=data
        return "The data is updated"
    @app.route("/data/<id>",methods=['DELETE'])
    def delete(id):
        states.pop(str(id))
        return "Hey your data got deleted"
if __name__=='__main__':
    app.run(debug=True)