from DB import DB as db

database = db()

print(database.select(entity='list', bool_op='AND', args={ 'id': 'jdas893kds81kdfhjas' }))

print(database.select(entity='list', bool_op='OR', args={ 'id': 'jdas893kds81kdfhjas', 'name': 'Testerson' }))

# lists_to_push = [
#     {
#         'id': 'jdas893kds81kdfhjas',
#         'name': 'Test List',
#         'description': 'Basically really only for testing'
#     },
#     {
#         'id': 'jfkleid9023ksdasdlk',
#         'name': 'Testus Testosteron',
#         'description': 'Weirdchamp Test'
#     },
#     {
#         'id': 'fadskjl8954kdsa2',
#         'name': 'Testerson',
#         'description': 'Meh'
#     }
# ]

# entries_to_push = [
#     {
#         'id': 'jlkf390jdfasil3jk',
#         'name': 'Test Entry',
#         'description': 'Basically really only for testing',
#         'list_id': 'jdas893kds81kdfhjas'
#     },
#     {
#         'id': 'jkl5239dsk230ö1l209',
#         'name': 'Test Entry 2',
#         'description': 'Just like the first one',
#         'list_id': 'jdas893kds81kdfhjas'
#     },
#     {
#         'id': 'fdasdsafuiekjasdlf109',
#         'name': 'Test Entry 3',
#         'description': 'Basically really only for testing',
#         'list_id': 'fadskjl8954kdsa2'
#     },
#     {
#         'id': 'jlkf390jdfasil3jk',
#         'name': 'Test Entry 4',
#         'list_id': 'jdas893kds81kdfhjas'
#     },
#     {
#         'id': 'jlkf390jdfasil3jk',
#         'name': 'Test Entry 5',
#         'description': 'Basically really only for testing',
#         'list_id': 'jdas893kds81kdfhjas'
#     },
#     {
#         'id': 'jlkf390jdfasil3jk',
#         'name': 'Test Entry 6',
#         'list_id': 'jdas893kds81kdfhjas'
#     }
# ]

# returned_from_insert = database.insert(entity='list', entries=lists_to_push)

# returned_from_insert = database.insert(entity='entry', entries=entries_to_push)

# print(database.select_all(entity='list'))
# print(database.select_all(entity='entry'))

# print('\n****************************************** TESTING SELECT NOW ******************************************\n')
# print(database.select(entity='list', bool_op='AND', args={ 'id': 'jdas893kds81kdfhjas', 'name': 'Testus Testosteron' }))

# print(database.select(entity='list', bool_op='OR', args={ 'id': 'jdas893kds81kdfhjas', 'name': 'Testus Testosteron' }))

# print('\n****************************************** TESTING UPDATE NOW ******************************************\n')

# print(database.select_all(entity='list'))

# database.update(entity='list', mapping={ 'name': 'Hello World' }, condition={ 'id': 'jfkleid9023ksdasdlk', }, bool_op='AND')

# print(database.select_all(entity='list'))

# print('\n****************************************** TESTING DELTE NOW ******************************************\n')
database.write_db_to_file()