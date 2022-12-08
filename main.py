# import MySQLdb
# from MySQLdb import Error
# import mysql.connector as mysql
import MySQLdb.cursors
from pathlib import Path
from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_restful import Resource, Api, reqparse
import pandas as pd


# creating a Flask app
app = Flask(__name__)
# creating an API object
api = Api(app)

# config Database login details, and create MySql object
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'toor'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'todosdb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


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


class LoginDb(Resource):
    def get(self):
        try:
            cursor = mysql.connection.cursor()
            print("Connected to database")
            return jsonify({'message': 'Initialised Database Successfully'})
        # If connection is not successful
        except (MySQLdb.Error, MySQLdb.Warning) as e:
            print(e)
            return jsonify({'message': 'Database Initialisation Failed'})


class Login(Resource):
    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('username', type=str, help='Sql Username')
            parser.add_argument('password', type=str, help='Sql Password')
            args = parser.parse_args()

            _userUser = args['username']
            _userPassword = args['password']

            return {'Username': args['username'], 'Password': args['password']}

        except Exception as e:
            return {'error': str(e)}


# Parse request for json, to create a task
class CreateTask(Resource):

    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('title', type=str, help='Title of Task to add')
            parser.add_argument('status', type=str, help='Completed status of Task to add')
            args = parser.parse_args()

            _taskTitle = args['title']
            _taskStatus = args['status']

            return {'Title': args['title'], 'Status': args['status']}

        except Exception as e:
            return {'error': str(e)}


def set_table(cur):
    try:
        cur.execute('DROP TABLE IF EXISTS tasklist')
        cur.execute('''CREATE TABLE tasklist (
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(100) NOT NULL,
                    completed BOOLEAN NOT NULL DEFAULT 0)''')
        cur.execute('''INSERT INTO tasklist (title) VALUES ('Test')''')
    except:
        print(f"Error: set_table error")
        return 0


# def execute_sql(cur, sql):
#     try:
#         cur.execute(sql)
#     except:
#         print(f"Error: '{err}'")
#         return 0


# URL route handlers
api.add_resource(LoginDb, '/logindb')
api.add_resource(Hello, '/home')
api.add_resource(Square, '/square/<int:num>')
api.add_resource(Login, '/login')
api.add_resource(CreateTask, '/createtask')


def main():
    app.run(host="localhost", port=int("5000"), debug=True)


if __name__ == '__main__':
    main()
