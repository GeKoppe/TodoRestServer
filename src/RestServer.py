from flask import Flask as f
from flask import jsonify as js
from flask import request
from flask import Response as resp
from DB import DB as db
import uuid

class RestServer:

    routes = None
    app = None

    host = ''
    port = 5000

    database = None

    def __init__(self, host='', port=5000) -> None:
        # Initialise the flask app and save host and port
        self.app = f(__name__)
        self.host = host
        self.port = port

        # Initialise the database
        self.database = db()

    ###
    #
    # Method get's called on bootup to add all endpoints to flask routing
    #
    ###
    def define_routes(self):
        # Endpoint config
        endpoints = [
            {
                'route': '/search',
                'name': 'search',
                'handler': self.search_list,
                'methods': ['GET']
            },
            {
                'route': '/todo-list/<id>',
                'name': 'delete',
                'handler': self.change_list,
                'methods': ['DELETE', 'PATCH', 'GET']
            },
            {
                'route': '/todo-list/<id>/entry',
                'name': 'add_entry',
                'handler': self.add_entry_to_list,
                'methods': ['POST']
            },
            {
                'route': '/todo-list',
                'name': 'add_list',
                'handler': self.add_list,
                'methods': ['POST', 'GET']
            },
            {
                'route': '/entry/<entry_id>',
                'name': 'update_entry',
                'handler': self.update_entry,
                'methods': ['PATCH', 'DELETE']
            },
            {
                'route': '/drop',
                'name': 'drop',
                'handler': self.drop,
                'methods': ['DELETE']
            }
        ]

        for ep in endpoints:
            self.app.add_url_rule(ep['route'], ep['name'], ep['handler'], methods=ep['methods'])
        
    ###
    # Method returns all existing todo-listsds
    #
    # @endpoint /todo-list GET
    ###
    def get_all_lists(self):
        return js({'entries': self.database.select_all(entity='list')})


    ###
    # @endpoint /search GET
    # 
    # @brief
    # GET: Method returns all lists with given name or list_id (name transmitted in query params)
    # 
    # @return {Dict[]} List of all lists matching the name (case insensitive)
    ###
    def search_list(self):
        name = ''
        
        # Check, if name or list id was given as query param and return 400, if neither was
        if not request.args.get('name') and not request.args.get('list_id'):
            return resp("{\"message\": \"Neither a name nor a list_id was given\"}", status=400, mimetype='application/json')
        
        # If name was given, make it lowercase in order to make it non case sensitive
        name = request.args.get('name')
        if name:
            name = name.lower()

        # Get all existing lists
        result = self.database.select_all(entity='list')

        # Iterate through all lists and push matching lists to an array in order to return
        correct_entries = []
        for entry in result:
            if entry['name'].lower() == name or entry['id'] == request.args.get('list_id'):
                correct_entries.append(entry)

        return js({
            'entries': correct_entries
        })

    ###
    # @endpoint /todo-list/<id> GET
    #
    # @brief
    # Method returns all entries in a given todo-list, specified in the url by the id. Only used as a callback, this was formerly it's
    # own endpoint
    #
    # @param {String} id: Is passed in the url. Specifies the todo-list of which the entries are supposed to be gotten
    # 
    # @return {Dict[]} List of all entries of a todo-list
    ###
    def get_entries_from_list(self, id):
        # Check, if id is an existing list_id. Return 400, if it isn't
        lists = self.database.select(entity='list', args={'id': id}, bool_op='AND')
        if len(lists) < 1:
            return resp("{\"message\": \"No list with id " + id + " found\"}", status=404, mimetype='application/json')
        
        # Get all entries for the list and return them in an array
        return js({'entries': self.database.select(entity='entry', args={ 'list_id': id }, bool_op='AND')})
    
    def drop(self):
        return js(self.database.drop())

    ###
    # @endpoint /todo-list/<id> GET; DELETE; PATCH
    #
    # @brief
    # GET: Method returns all entries in a given todo-list, specified in the url by the id.
    # DELETE: The list with given id is deleted, as well as all entries with that list_id
    # PATCH: The list with given id is updated. Name must be transmitted in request body
    #
    # @return {Dict[]} List of all entries of a todo-list
    ###
    def change_list(self, id):
        result = {}

        # Check, if a list with given id exists. If not, return 404
        lists = self.database.select(entity='list', args={'id': id}, bool_op='AND')
        if len(lists) < 1:
            return resp("{\"message\": \"No list with id " + id + " found\"}", status=404, mimetype='application/json')
        
        if request.method == 'GET':
            # If request method was GET; return all entries for list corresponding to id
            return self.get_entries_from_list(id)
        if request.method == 'DELETE':
            # If request method was delete, delete list
            result = self.database.delete(entity='list', condition={'id': id}, bool_op='AND')
            if result['deleted'] < 1:
                return resp("{\"message\": \"Failed to delete list\"}", status=500, mimetype='application/json')

            # Get entries for list to check, whether any entries need to be deleted
            result = self.database.select(entity='entry', args={'list_id': id}, bool_op='AND')
            if len(result) > 0:
                # If there are entries, delete them. If that didn't work, return 500
                result = self.database.delete(entity='entry', condition={'list_id': id}, bool_op='AND')
                if result['deleted'] < 1:
                    return resp("{\"message\": \"Successful in deleting list, failed to delete it's entries\"}", status=500, mimetype='application/json')

            # Return 200
            return resp("{\"message\": \"Deletion successful\"}", status=200, mimetype='application/json')
        elif request.method == 'PATCH':
            # Patch request method means, that the list is supposed to be updated
            name = ''

            # Try to get the name from form data
            if not not request.form.get('name'):
                name = request.form.get('name')

            # If name wasn't in form data, try to get it from json
            if name == '':
                try:
                    name = request.json['name']
                except:
                    pass

            # If there is still no name, return 400
            if name == '':
                return resp("{\"message\": \"No new name given\"}", status=400, mimetype='application/json')
            
            # Update the list, check, if update was written and return 200, if it was, 500 otherwise
            arguments = {
                'name': name
            }
            result = self.database.update(entity='list', mapping=arguments, condition={'id': id}, bool_op='AND')
            if result['entries_updated'] < 1:
                return resp("{\"message\": \"Failed to update\"}", status=500, mimetype='application/json')

            return resp("{\"message\": \"Update successful\"}", status=200, mimetype='application/json')
        elif request.method == 'GET':
            # If method was get, return all entries from that list
            list = self.database.select(entity='entry', args={'list_id': id}, bool_op='AND')
            return js({'entries': list})
        return result
    

    ###
    # @endpoint /todo-list GET; POST
    # 
    # @brief
    # GET: Retrieves all existing lists
    # POST: Adds a list, using the parameters transmitted in body of request
    #
    # @return {Dict} Information about the added list
    ###
    def add_list(self):
        name = ''

        if request.method == 'GET':
            return self.get_all_lists()

        # Check, if necessary body parameter was passed and return bad status code, if it wasn't
        if not request.form.get('name'):
            try:
                name = request.json['name']
            except:
                return resp("{\"message\": \"No name was given\"}", status=400, mimetype='application/json')
            
        else:
            if request.form.get('name'):
                name = request.form.get('name')
            else:
                try:
                    name = request.json['name']
                except:
                    return resp("{\"message\": \"No name was given\"}", status=400, mimetype='application/json')
                
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
        }

        # Insert the new todo-list into the database
        result = self.database.insert(entity='list', entries=[arguments])
        if result['written'] < 1:
            return resp("{\"message\": \"Failed to Insert\"}", status=500, mimetype='application/json')
        return js({'entries': [arguments]})

    ###
    # @endpoint /entry/<entry_id> PATCH; DELETE
    # 
    # @brief
    # PATCH: Updates entry with id entry_id. name or description must be given in request body
    # DELETE: Entry with id entry_id is deleted
    #
    # @return statuscode
    ###
    def update_entry(self, entry_id):
        result = {}

        # Check, whether an entry with given id exists and return 404 if there is none
        entries = self.database.select(entity='entry', args={'id': entry_id}, bool_op='AND')
        if len(entries) < 1:
            return resp("{\"message\": \"No entry with id " + entry_id + " found\"}", status=404, mimetype='application/json')
        
        if request.method == 'PATCH':
            # If request method is patch, the entry is supposed to be updated
            name = ''
            description = ''

            # try to get the name from form-data and json
            if not not request.form.get('name'):
                name = request.form.get('name')

            if not name:
                try:
                    name = request.json['name']
                except:
                    pass
            
            # try to get the description from form-data and json
            if not not request.form.get('description'):
                description = request.form.get('description')

            if not description:
                try:
                    description = request.json['description']
                except:
                    pass

            # If neither name nor description was given, return 400
            if name == '' and description == '':
                return resp("{\"message\": \"No entries updated, as no parameters were given\"}", status=400, mimetype='application/json')
            
            # Update the entry
            arguments = {
                'name': name,
                'description': description
            }
            result = self.database.update(entity='entry', mapping=arguments, condition={'id': entry_id}, bool_op='AND')
            
            # If no entries were updated, something went wrong, return 500, else return 200
            if result['entries_updated'] < 1:
                return resp("{\"message\": \"Failed to update\"}", status=500, mimetype='application/json')
            
            return resp("{\"message\": \"Update successful\"}", status=200, mimetype='application/json')
        elif request.method == 'DELETE':
            # delete entry from database
            result = self.database.delete(entity='entry', condition={'id': entry_id})

            # If no entry was deleted, return 500 as something went wrong, else return 200
            if result['deleted'] < 1:
                return resp("{\"message\": \"Failed to delete\"}", status=500, mimetype='application/json')
            return resp("{\"message\": \"Deletion successful\"}", status=200, mimetype='application/json')
        
        return resp("{\"message\": \"Unexpected error\"}", status=500, mimetype='application/json')
    
    ###
    # @endpoint /todo-list/<id>/entry POST
    # 
    # @brief
    # POST: Adds an entry to the list specified by id. At least name of new entry must be given in request body
    #
    # @return {Dict}
    ###
    def add_entry_to_list(self, id):
        name = ''
        description = ''

        # Check, whether list with id exists and return 404, if there is none
        lists = self.database.select(entity='list', args={'id': id}, bool_op='AND')
        if len(lists) < 1:
            return resp("{\"message\": \"No list with id " + id + " found\"}", status=404, mimetype='application/json')

        # Get name from request body, return 400 if no name was given
        if not request.form.get('name'): 
            try:
                name = request.json['name']
            except:
                return resp("{\"message\": \"No name for new entry given\"}", status=400, mimetype='application/json')
        else:
            name = request.form.get('name')

            if not name:
                name = request.json['name']

        if name == '':
            return resp("{\"message\": \"No name for new entry given\"}", status=400, mimetype='application/json')
        # Get description from message body. Set to empty string, if it doesn't exist
        if not not request.form.get('description'):
            description = request.form.get('description')

        if not description:
            try:
                description = request.json['description']
            except:
                description = ''

        # Generate a new uuid for the new list and check the database for existing entries
        new_id = str(uuid.uuid4())
        check = self.database.select(entity='list', args={'id': new_id})
        
        # If the check yielded results (highly unlikely), create a new uuid and try again
        while len(check) > 0:
            new_id = str(uuid.uuid4())
            check = self.database.select(entity='entry', args={'id': new_id})

        # Insert new entry into database. Return 500, if something went wrong, information about new entry otherwise
        arguments = {
            'name': name,
            'description': description,
            'list_id': id,
            'id': new_id
        }

        result = self.database.insert(entity='entry', entries=[arguments])
        if result['written'] < 1:
            return resp("{\"message\": \"Failed to Insert\"}", status=500, mimetype='application/json')

        return js({'entries': result['entries']})


    def boot(self):    
        self.define_routes()
        self.app.run(host=self.host, port=self.port)