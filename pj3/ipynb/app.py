from flask import Flask, request

app = Flask(__name__)

@app.route('/headers')
def headers():
    # @TODO unpack the request header
    header = request.headers(['Authorization'])
    token = header.split(' ')[1]
    print(token)
    return 'not implemented'
