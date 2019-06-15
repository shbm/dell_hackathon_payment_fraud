from flask import Flask, request, jsonify
from flask_pymongo import PyMongo, ObjectId

app = Flask(__name__)

mlab_uri = 'mongodb://root:123456seven@ds125602.mlab.com:25602/todo'
local_uri = 'mongodb://localhost/todo'

app.config['MONGO_DBNAME'] = 'todo'
app.config['MONGO_URI'] = local_uri

mongo = PyMongo(app)


@app.route('/todo/api/v1.0/tasks', methods=['GET', 'POST'])
def tasks():
    if request.method == 'GET':
        unserialize_tasks = mongo.db.tasks.find({})
        serialize_tasks = []
        for task in unserialize_tasks:
            serialize_tasks.append({
                'id': str(task['_id']),
                'title': task['title'],
                'description': task['description'],
                'done': task['done']
            })
        return jsonify(serialize_tasks)

    elif request.method == 'POST':
        try:
            task = {
                'title': request.json['title'],
                'description': request.json['description'],
                'done': False
            }
            id = mongo.db.tasks.insert(task)
            return jsonify({'status': 'Success', '_id': str(id)})
        except KeyError:
            return jsonify({'status': 'Missing title or discription, or both.'})


@app.route('/todo/api/v1.0/tasks/<task_id>', methods=['GET', 'PUT', 'DELETE'])
def task(task_id):
    if request.method == 'GET':
        if is_task_present(task_id):
            task = get_task(task_id)
            return jsonify(task)
        else:
            return jsonify({'status': 'There is no task with _id: ' + task_id})

    elif request.method == 'PUT':
        if is_task_present(task_id):
            if not request.json:
                return jsonify({'status': 'Please provide atleast one key, value to update'})
            old_task = {}
            old_task = get_task(task_id)
            old_task['_id'] = ObjectId(old_task['_id'])
            updated_task = {}
            for key in old_task.keys():
                try:
                    updated_task[key] = request.json[key]
                except:
                    updated_task[key] = old_task[key]
            mongo.db.tasks.save(updated_task)
            return jsonify({'status': 'Success'})
        else:
            return jsonify({'status': 'There is no task with _id: ' + task_id})

    elif request.method == 'DELETE':
        if is_task_present(task_id):
            mongo.db.tasks.remove({'_id': ObjectId(task_id)})
            return jsonify({'status': 'Success'})
        else:
            return jsonify({'status': 'There is no task with _id: ' + task_id})
    else:
        pass


def is_task_present(task_id):
    try:
        task_cursor = mongo.db.tasks.find_one({'_id': ObjectId(task_id)})
    except:
        return False
    if task_cursor:
        return True
    else:
        False


def get_task(task_id):
    task_cursor = mongo.db.tasks.find_one({'_id': ObjectId(task_id)})
    if task_cursor:
        task = {
            '_id': str(task_cursor['_id']),
            'title': task_cursor['title'],
            'description': task_cursor['description'],
            'done': task_cursor['done']
        }
    return task


if __name__ == '__main__':
    app.run(debug=True)

