import MySQLdb
from MySQLdb import Error
import MySQLdb.cursors

from flask import Flask, jsonify, request, redirect, url_for
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
app.config['MYSQL_DB'] = 'py_tasks'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

# sql conn with no named database, to allow creating of named database before route setting
connection = None
cursor = None
try:
    connection = MySQLdb.connect(host="localhost",  # your host, usually localhost
                                 user="root",  # your username
                                 passwd="toor",  # your password
                                 db="")
    cursor = connection.cursor()
    try:
        cursor.execute('CREATE DATABASE IF NOT EXISTS py_tasks')
        cursor.execute('USE py_tasks')
        cursor.execute('DROP TABLE IF EXISTS tasklist')
        cursor.execute('''CREATE TABLE tasklist (
                    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(100) NOT NULL,
                    completed BOOLEAN NOT NULL DEFAULT 0)''')
        cursor.execute('''INSERT INTO tasklist (title) VALUES ('Test')''')
        connection.commit()
        cursor.close()

    except MySQLdb.Error as err:
        print(f"Error: '{err}'")

except MySQLdb.Error as err:
    print(f"Error: '{err}'")
finally:
    connection.close()


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

            if _taskStatus:
                _taskStatus = 1
            else:
                _taskStatus = 0

            cur = mysql.connection.cursor()
            cur.execute('''INSERT INTO tasklist (title, completed) VALUES (%s, %s)''', (_taskTitle, str(_taskStatus)))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('alltasks'))
            # return {'Title': args['title'], 'Status': args['status']}

        except Exception as e:
            return {'error': str(e)}


class AllTasks(Resource):

    def get(self):
        print("Getting all tasks")
        try:
            cur = mysql.connection.cursor()
            cur.execute('''SELECT * FROM tasklist WHERE id IS NOT NULL''')
            all_tasks = cur.fetchall()
            if all_tasks:
                for task in all_tasks:
                    print(task)
        except Exception as e:
            return {'error': str(e)}


    def post(self):
        print("Adding new task")


class TaskDetail(Resource):

    def get(self):
        print("Getting details for single Task")

    def post(self):
        print("Updating details for Task")


# def execute_sql(cur, sql):
#     try:
#         cur.execute(sql)
#     except:
#         print(f"Error: '{err}'")
#         return 0


# URL route handlers
api.add_resource(Hello, '/home')
api.add_resource(Square, '/square/<int:num>')
api.add_resource(Login, '/login')
api.add_resource(CreateTask, '/createtask')
api.add_resource(AllTasks, '/alltasks')
api.add_resource(TaskDetail, '/task')


def main():
    app.run(host="localhost", port=int("5000"), debug=True)


if __name__ == '__main__':
    main()
