from flask import Flask as f
from flask import jsonify as js
from DB import DB as db

class RestServer:

    routes = None
    app = None

    host = ''
    port = 5000

    database = None

    endpoint_handlers = []

    def __init__(self, host='', port=5000) -> None:
        self.app = f(__name__)
        self.host = host
        self.port = port
        self.database = db()

        lists_to_push = [
            {
                'id': 'jdas893kds81kdfhjas',
                'name': 'Test List',
                'description': 'Basically really only for testing'
            },
            {
                'id': 'jfkleid9023ksdasdlk',
                'name': 'Testus Testosteron',
                'description': 'Weirdchamp Test'
            },
            {
                'id': 'fadskjl8954kdsa2',
                'name': 'Testerson',
                'description': 'Meh'
            }
        ]

        entries_to_push = [
            {
                'id': 'jlkf390jdfasil3jk',
                'name': 'Test Entry',
                'description': 'Basically really only for testing',
                'list_id': 'jdas893kds81kdfhjas'
            },
            {
                'id': 'jkl5239dsk230ö1l209',
                'name': 'Test Entry 2',
                'description': 'Just like the first one',
                'list_id': 'jdas893kds81kdfhjas'
            },
            {
                'id': 'fdasdsafuiekjasdlf109',
                'name': 'Test Entry 3',
                'description': 'Basically really only for testing',
                'list_id': 'fadskjl8954kdsa2'
            },
            {
                'id': 'fdasjkle',
                'name': 'Test Entry 4',
                'list_id': 'jdas893kds81kdfhjas'
            },
            {
                'id': '8d923okldsfuzoi21',
                'name': 'Test Entry 5',
                'description': 'Basically really only for testing',
                'list_id': 'jdas893kds81kdfhjas'
            },
            {
                'id': '10fdspj3219i012',
                'name': 'Test Entry 6',
                'list_id': 'jdas893kds81kdfhjas'
            }
        ]

        self.database.insert(entity='list', entries=lists_to_push)

        self.database.insert(entity='entry', entries=entries_to_push)


    def define_routes(self):
        self.app.add_url_rule('/lists', 'lists', self.get_lists, methods=['GET'])
        
    
    def get_lists(self):
        return js(self.database.select_all(entity='list'))

    def get_entries(self):
        pass

    def boot(self):
        self.define_routes()
        self.app.run(host=self.host, port=self.port)