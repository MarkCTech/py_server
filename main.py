import MySQLdb.cursors
from flask import Flask, jsonify, request, redirect, url_for
from flask_mysqldb import MySQL
from flask_restful import Resource, Api, reqparse


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
            print(str(e))
            return {'error': "Could not log in"}


class AllTasks(Resource):

    def get(self):
        print("Getting all tasks")
        try:
            cur = mysql.connection.cursor()
            cur.execute('''SELECT * FROM tasklist WHERE id IS NOT NULL''')
            all_tasks = cur.fetchall()
            if all_tasks:
                return jsonify(all_tasks)
        except Exception as e:
            print(str(e))
            return {'error': "Could not get all Tasks"}

    def post(self):
        # Parse request for json, to create a task
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
            cur.execute('''INSERT INTO tasklist (title, completed) VALUES (%s, %s)''',
                        (_taskTitle, str(_taskStatus)))

            # Save sql work, close and load /alltasks
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('alltasks'))
            # return {'Title': args['title'], 'Status': args['status']}

        except Exception as e:
            print(str(e))
            return {'error': "Could not post Task"}


class TaskDetail(Resource):

    def get(self, task_id):
        print("Getting details for Task by ID")
        try:
            cur = mysql.connection.cursor()
            cur.execute('''SELECT * FROM tasklist WHERE id IS NOT NULL AND id = %s''', str(task_id))
            all_tasks = cur.fetchall()

            if all_tasks:
                return jsonify(all_tasks)
        except Exception as e:
            print(str(e))
            return {'error': "Could not get Task by ID"}

    def put(self, task_id):
        print("Updating details for Task")
        try:

            parser = reqparse.RequestParser()
            parser.add_argument('title', type=str, help='Title of Task to update')
            parser.add_argument('status', type=str, help='Completed status of Task')
            args = parser.parse_args()

            _taskTitle = args['title']
            _taskStatus = args['status']

            if _taskStatus:
                _taskStatus = str(1)
            else:
                _taskStatus = str(0)

            cur = mysql.connection.cursor()
            update_user_cmd = '''UPDATE tasklist SET title=%s, completed=%s WHERE id=%s'''
            cur.execute(update_user_cmd, (_taskTitle, _taskStatus, str(task_id)))

            # Save sql work, close and load /alltasks
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('alltasks'))

        except Exception as e:
            print(str(e))
        return {'error': "Could not update Task details"}

    def delete(self, task_id):
        print("Attempting to delete Task by ID")
        try:
            cur = mysql.connection.cursor()
            cur.execute('''DELETE FROM tasklist WHERE id=%s''', str(task_id))

            # Save sql work, close and load /alltasks
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('alltasks'))

        except Exception as e:
            print(str(e))
            return {'error': "Could not update Task details"}


class StaticServe(Resource):
    def get(self):
        return app.send_static_file('index.html')


def init_mysql_api_app():
    # sql conn with no named database, to allow creating of named database before route setting
    connection = None
    cursor = None
    print("\nInitializing database...")
    password = input("Root Password: ")
    try:
        connection = MySQLdb.connect(host="localhost",  # your host, usually localhost
                                     user="root",  # your username
                                     passwd=password,  # your password
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
        # Close root connection
        connection.close()
        print("Created workspace with py_tasks database")

        # creating a Flask app
        global app
        app = Flask(__name__, static_folder='./react/task_app/build', static_url_path='/')

        # creating an API object
        global api
        api = Api(app)

        # config Flasks Database login details
        print("\nLogin to database as a user:")
        database = "py_tasks"
        username = input("Username: ")
        password = input("Password: ")
        app.config['MYSQL_USER'] = username
        app.config['MYSQL_PASSWORD'] = password
        app.config['MYSQL_HOST'] = 'localhost'
        app.config['MYSQL_DB'] = database
        app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

        # create MySql object
        global mysql
        mysql = MySQL(app)

        # URL route handlers
        api.add_resource(StaticServe, '/')
        api.add_resource(Hello, '/home')
        api.add_resource(Square, '/square/<int:num>')
        api.add_resource(Login, '/login')
        api.add_resource(AllTasks, '/alltasks')
        api.add_resource(TaskDetail, '/task/<int:task_id>')


def main():

    init_mysql_api_app()
    # Run flask                                                
    app.run(host="localhost", port=int("5000"), debug=True, use_reloader=False)


if __name__ == '__main__':
    main()
    