import MySQLdb
from MySQLdb import Error
import mysql.connector as mysql
from pathlib import Path
from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_restful import Resource, Api, reqparse
import pandas as pd


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
    except Error as err:
        print(f"Error: '{err}'")
        return 0


def execute_sql(cur, sql):
    try:
        cur.execute(sql)
    except Error as err:
        print(f"Error: '{err}'")
        return 0


def mysql_connect():
    # Trying to connect
    try:
        db_connection = MySQLdb.connect("localhost", "root", "toor", "todosdb")
        db_connection.autocommit(True)
    # If connection is not successful
    except Error as err:
        print("Can't connect to database")
        print(f"Error: '{err}'")
        return 0
    # If Connection Is Successful
    print("Connected")

    # Making Cursor Object For Query Execution
    cursor = db_connection.cursor()
    # Executing Query
    set_table(cursor)
    # Closing Database Connection
    cursor.close()
    db_connection.close()


def flask_config(app):
    # config Database login details, and create MySql object
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'toor'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_DB'] = 'todosdb'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    flask_mysql = MySQL(app)
    return flask_mysql


def init_flask_sql():
    # creating a Flask app
    app = Flask(__name__)
    # creating an API object
    api = Api(app)

    mysql_connect()

    # URL route handlers
    api.add_resource(Hello, '/')
    api.add_resource(Square, '/square/<int:num>')
    api.add_resource(Login, '/login')
    api.add_resource(CreateTask, '/createtask')

    app.run(debug=True)


def main():
    init_flask_sql()


if __name__ == '__main__':
    main()
