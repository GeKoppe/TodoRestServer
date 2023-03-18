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
            },
            {
                'route': '/entry/<list_id>/<entry_id>',
                'name': 'update_entry',
                'handler': self.update_entry,
                'methods': ['POST', 'DELETE']
            }
        ]

        for ep in endpoints:
            self.app.add_url_rule(ep['route'], ep['name'], ep['handler'], methods=ep['methods'])
        
    
    def get_all_lists(self):
        return js(self.database.select_all(entity='list'))


    ###
    # @endpoint /search
    #
    # @brief
    # Method returns all lists with given name (name transmitted in request body)
    # 
    # @return {Dict[]} List of all lists matching the name (case insensitive)
    ###
    def search_list(self):
        name = ''
        
        if not request.args.get('name'):
            # TODO return bad status code
            pass
        
        name = request.args.get('name').lower()

        result = self.database.select_all(entity='list')

        correct_entries = []
        for entry in result:
            if entry['name'].lower() == name:
                correct_entries.append(entry)

        return js(correct_entries)

    ###
    # @endpoint /todo-list/<id>/entries
    #
    # @brief
    # Method returns all entries in a given todo-list, specified in the url by the id.
    #
    # @param {String} id: Is passed in the url. Specifies the todo-list of which the entries are supposed to be gotten
    # 
    # @return {Dict[]} List of all entries of a todo-list
    ###
    def get_entries_from_list(self, id):
        return js(self.database.select(entity='entry', args={ 'list_id': id }, bool_op='AND'))
    
    ###
    # @endpoint /todo-list/<id>/entries
    #
    # @brief
    # Method returns all entries in a given todo-list, specified in the url by the id.
    #
    # @return {Dict[]} List of all entries of a todo-list
    ###
    def delete(self, id):
        result = self.database.delete(entity='list', condition={'id': id}, bool_op='AND')
        self.database.delete(entity='entry', condition={'list_id': id}, bool_op='AND')
        return result
    

    ###
    # @endpoint /todo-list
    # 
    # @brief
    # Adds a list, using the parameters transmitted in body of request
    #
    # @return {Dict} Information about the added list
    ###
    def add_list(self):
        name = ''
        description = ''

        # Check, if necessary body parameter was passed and return bad status code, if it wasn't
        if not request.form.get('name'):
            # TODO return bad status code, some 300 stuff I guess
            pass
        else:
            name = request.form.get('name')

        if not not request.form.get('description'):
            description = request.form.get('description')

        # Generate a new uuid for the new list and check the database for existing entries
        new_id = str(uuid.uuid4())
        check = self.database.select(entity='list', args={'id': new_id})
        
        # If the check yielded results (highly unlikely), create a new uuid and try again
        while len(check) > 0:
            new_id = str(uuid.uuid4())
            check = self.database.select(entity='list', args={'id': new_id})
        
        # Pack arguments into dict
        arguments = {
            'id': new_id,
            'name': name,
            'description': description
        }

        # Insert the new todo-list into the database
        result = self.database.insert(entity='list', entries=[arguments])
        return js(result)


    def update_entry(self, list_id, entry_id):
        result = {}
        if request.method == 'POST':
                
            name = ''
            description = ''

            if not not request.form.get('name'):
                name = request.form.get('name')

            if not not request.form.get('description'):
                description = request.form.get('description')
            
            arguments = {
                'name': name,
                'description': description
            }

            if name == '' and description == '':
                pass
            
            result = self.database.update(entity='entry', mapping=arguments, condition={'id': entry_id, 'list_id': list_id}, bool_op='AND')
        elif request.method == 'DELETE':
            result = self.database.delete(entity='entry', condition={'id': entry_id, 'list_id': list_id})
            
        return js(result)
    
    def add_entry_to_list(self):
        name = ''
        description = ''
        list_id = ''

        if not request.form.get('name') or not request.form.get('list_id'):
            pass
        else:
            name = request.form.get('name')
            list_id = request.form.get('list_id')

        if not not request.form.get('description'):
            description = request.form.get('description')

        # Generate a new uuid for the new list and check the database for existing entries
        new_id = str(uuid.uuid4())
        check = self.database.select(entity='list', args={'id': new_id})
        
        # If the check yielded results (highly unlikely), create a new uuid and try again
        while len(check) > 0:
            new_id = str(uuid.uuid4())
            check = self.database.select(entity='entry', args={'id': new_id})

        arguments = {
            'name': name,
            'description': description,
            'list_id': list_id,
            'id': new_id
        }

        return js(self.database.insert(entity='entry', entries=[arguments]))


    def boot(self):    
        self.define_routes()
        self.app.run(host=self.host, port=self.port)