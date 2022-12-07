from flask import Flask, jsonify, request
from flask_restful import Resource, Api

# creating a Flask app
app = Flask(__name__)
# creating an API object
api = Api(app)


# returns hello world when we use GET.
# returns the data that we send when we use POST.
class Hello(Resource):

    def get(self):
        return jsonify({'message': 'Hello'})

    def post(self):
        data = request.get_json()
        return jsonify({'data': data}), 201


# A simple function to calculate the square of a number
class Square(Resource):

    def get(self, num):
        return jsonify({'square': num ** 2})


# URL route handlers
api.add_resource(Hello, '/')
api.add_resource(Square, '/square/<int:num>')


if __name__ == '__main__':
    app.run(debug=True)
