from flask import Flask as f
from flask import jsonify as js
from flask import request
from DB import DB as db
import uuid

class RestServer:

    routes = None
    app = None

    host = ''
    port = 5000

    database = None

    def __init__(self, host='', port=5000) -> None:
        self.app = f(__name__)
        self.host = host
        self.port = port
        self.database = db()

    def define_routes(self):
        endpoints = [
            {
                'route': '/todo-list/<id>/entries',
                'name': 'todo_list_entries',
                'handler': self.get_entries_from_list,
                'methods': ['GET']
            },
            {
                'route': '/search',
                'name': 'search',
                'handler': self.search_list,
                'methods': ['GET']
            },
            {
                'route': '/todo-list/<id>',
                'name': 'delete',
                'handler': self.delete,
                'methods': ['DELETE']
            },
            {
                'route': '/entry',
                'name': 'add_entry',
                'handler': self.add_entry_to_list,
                'methods': ['POST']
            },
            {
                'route': '/todo-list',
                'name': 'add_list',
                'handler': self.add_list,
                'methods': ['PUT']
            }
        ]

        for ep in endpoints:
            self.app.add_url_rule(ep['route'], ep['name'], ep['handler'], methods=ep['methods'])
        
    
    def get_all_lists(self):
        return js(self.database.select_all(entity='list'))

    def search_list(self):
        arguments = {}
        
        if not request.args.get('name') == '':
            arguments['name'] = request.args.get('name')

        if not request.args.get('description') == '':
            arguments['description'] = request.args.get('name')

        result = {}

        if len(arguments) > 0:
            result = self.database.select(entity='list', args=arguments, bool_op='OR')
        else:
            result = self.database.select_all(entity='list')

        return js(result)

    def get_entries_from_list(self, id):
        return js(self.database.select(entity='entry', args={ 'list_id': id }, bool_op='AND'))
    
    def delete(self, id):
        result = self.database.delete(entity='list', condition={'id': id}, bool_op='AND')
        self.database.delete(entity='entry', condition={'list_id': id}, bool_op='AND')
        return result
    

    def add_list(self):
        name = ''
        description = ''

        if not request.form.get('name'):
            # TODO return bad status code, some 300 stuff I guess
            pass
        else:
            name = request.form.get('name')

        if request.form.get('description'):
            description = request.form.get('description')

        new_id = uuid.uuid4()
        arguments = {
            'id': str(new_id),
            'name': name,
            'description': description
        }

        result = self.database.insert(entity='list', entries=[arguments])
        return js(result)
    
    def add_entry_to_list(self):
        # TODO UUID Generieren
        body = request.form



    def boot(self):    
        self.define_routes()
        self.app.run(host=self.host, port=self.port)