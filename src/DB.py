import os
import json

class DB:

    list = None
    entry = None
    
    list_attributes = [
        'id',
        'name',
        'description'
    ]

    entry_attributes = [
        'id',
        'name',
        'description',
        'list_id'
    ]

    def __init__ (self) -> None:
        current_dir = os.getcwd()
        final_dir = os.path.join(current_dir, r'database')

        if not os.path.exists(final_dir + '\\db.json'):
            self.list = []
            self.entry = []
        else:
            try:
                db_file = open(final_dir + '\\db.json', 'r')
                db_json = json.loads(db_file.read())
                self.list = db_json['list']
                self.entry = db_json['entry']
            except:
                self.list = []
                self.entry = []
        
    

    def select(self, entity=None, args=None, bool_op='AND'):
        if not entity or not args:
            raise RuntimeError('No type or arguments given')

        if not (entity == 'list' or entity == 'entry'):
            raise RuntimeError('Type of entity not specified correctly.')
        
        for arg in args:
            if entity == 'list':
                if not (arg in self.list_attributes):
                    raise RuntimeError(entity + ' does not have attribute ' + arg)
            
            if entity == 'entry':
                if not (arg in self.entry_attributes):
                    raise RuntimeError(entity + ' does not have attribute ' + arg)
        
        num_of_args = 0
        
        for arg in args:
            num_of_args += 1

        if num_of_args == 0:
            if entity == 'list':
                return self.list
            else:
                return self.entry

        results = []

        if entity == 'list':
            for entry in self.list:
                args_matching = 0
                for arg in args:
                    if entry[arg] == args[arg]:
                        if bool_op == 'AND': 
                            args_matching += 1
                        elif bool_op == 'OR':
                            results.append(entry)
                
                if args_matching == num_of_args:
                    results.append(entry)
        
        return results

    ###
    #   @brief
    #   Inserts new values into the database. Both entity and entries are necessary.
    #   Entity is either 'list', if you want to add a new to do list or 'entry', if you want to add a new entry for a todo list
    #   Every part of the entries argument needs to be a dictionary.
    #   If entity is set as 'list', all entries need to have a name and an id property
    #   If entity is set as 'entry', all entries need to have a name and an id property, as well as a 'list_id' property
    #
    #   @param {String} entity: either list
    #   @param {Dictionary[]} entries: Dictionaries of all values that are to be inserted into
    #                                   into the database. For both 
    #
    ###
    def insert(self, entity=None, entries=None):
        # Check, if both arguments are given.
        if not entity or not entries:
            raise RuntimeError('No type or arguments given')
        
        # Check, if entity was specified correctly as either entry or list
        if not (entity == 'list' or entity == 'entry'):
            raise ValueError('Type of entity not specified correctly.')
        
        # iterate through all entries to see, if necessary arguments are set
        for entry in entries:
            # Check, if connection to a certain list was made.
            if entity == 'entry':
                if (not 'list_id' in entry) or entry['list_id'] == '':
                    raise RuntimeError('No list_id given for one entry.')

            # For both entries and lists, name and id are necessary so check if they are given
            if ((not 'name' in entry) or entry['name'] == '') and ((not 'id' in entry) or entry['id'] == ''):
                raise ValueError('Necessary Arguments not given.')
        
        # initialize counters to check, how many lines were written
        entries_written = 0
        total_entries = len(entries)
        entry_index = 0
        written_entries = []

        for entry in entries:
            if entity == 'list':
                for l in self.list:
                    if entry['id'] == l['id']:
                        raise ValueError('ID ' + entry['id'] + ' already exists in list.')
                    
            if entity == 'entry':
                for l in self.entry:
                    if entry['id'] == l['id']:
                        raise ValueError('ID ' + entry['id'] + ' already exists in entry.')
            
            s_entry_index = 0
            for e in entries:
                if entry['id'] == e['id'] and not (entry_index == s_entry_index):
                    raise ValueError('Trying to pass ID ' + entry['id'] + ' two or more times.')
                s_entry_index += 1
            entry_index += 1
        
        # iterate through all the entries again and push them into the databse
        for entry in entries:
            # everything is copied into a new dict, in order to filter out every unnecessary property
            dict_to_push = {}
            if not ('description' in entry) or entry['description'] == '':
                dict_to_push['description'] = ''
            else:
                dict_to_push['description'] = entry['description']

            dict_to_push['id'] = entry['id']
            dict_to_push['name'] = entry['name']

            if entity == 'entry':
                dict_to_push['list_id'] = entry['list_id']
                entries_written += 1
                written_entries.append(dict_to_push)
                self.entry.append(dict_to_push)

            if entity == 'list':
                entries_written += 1
                written_entries.append(dict_to_push)
                self.list.append(dict_to_push)

        self.write_db_to_file()
        return { 'written': entries_written, 'total': total_entries, 'entries': written_entries}
    

    ###
    # 
    # @brief
    # Selects all entries from the specified entity
    #
    # @param {String} entity: Entity from which all entries are to be retrieved. Mus be either 'list' or 'entry'
    #
    # @return {Dictionary[]} All entries in the specified list
    #
    ###
    def select_all (self, entity=None):
        # Check if entity was passed to the function
        if not entity or entity == '':
            raise ValueError('No entity given')

        # Return the corresponding list
        if entity == 'list':
            return self.list
        elif entity == 'entry':
            return self.entry
        else:
            # If entity was neither list nor entry, raise an error
            raise ValueError(entity + ' does not exist')

    ###
    # 
    # @brief
    # Updates all entries that match the specified condition. For those entries, the properties will be set as defined in
    # the mapping parameter. If a property wasn't defined in mapping, it won't be changed
    #
    # @param {String} entity: Entity from which all entries are to be retrieved. Mus be either 'list' or 'entry'
    # @param {Dictionary} mapping: Defines, how the matching entries should be updated. Keys are properties to be updated, values are 
    #                               what is set. If a key is used, that isn't defined for that entity, an error is raised
    #                               Example:    {
    #                                               'name': 'New name that will be set for all entries that match the conditions'
    #                                           }
    # @param {Dictionary} condition (optioanl): Defines which entries should be updated. Only entries having the properties defined in condition are updated.
    #                                           Dictionary looks the same as in mapping.
    #                                           If no conditions are given, every single entry of given entity is updated. Use with care.
    # @param {String} bool_op: Either 'AND' or 'OR'. If 'AND' is passed, entries must match ALL conditions. If 'OR' is passed, entries must only
    #                           match one condition
    #
    # @return {Dictionary[]} All entries in the specified list
    #
    ###
    def update(self, entity=None, mapping=None, condition=None, bool_op='AND'):
        # Check, if all params are given and done correctly. Raise lots of errors otherwise
        if not entity or entity == '':
            raise RuntimeError('No entity given.')
        
        if not (entity == 'list' or entity == 'entry'):
            raise ValueError('Type of entity not specified correctly.')

        if not mapping:
            raise RuntimeError('No mapping given.')
        
        if not bool_op or not (bool_op == 'OR' or bool_op == 'AND'):
            raise RuntimeError('bool_op must either be AND or OR.')
        
        if entity == 'list':
            for key in mapping:
                if not key in self.list_attributes:
                    raise ValueError('Lists do not have attribute ' + key)
            
            if not not condition:
                for key in condition:
                    if not key in self.list_attributes:
                        raise ValueError('Lists do not have attribute ' + key)
        
        if entity == 'entry':
            for key in mapping:
                if not key in self.entry_attributes:
                    raise ValueError('Entries do not have attribute ' + key)
            
            if not not condition:
                for key in condition:
                    if not key in self.entry_attributes:
                        raise ValueError('Entries do not have attribute ' + key)
        
        for map in mapping:
            if map == 'id':
                raise ValueError('Cannot update IDs!')
            
        # Check how many conditions exist for future reference
        num_of_conditions = 0
        if not not condition:
            for key in condition:
                num_of_conditions += 1

        # Counter for the return json
        num_of_entries_updated = 0

        # Iterate through the list
        if entity == 'list':
            for entry in self.list:
                # If a condition is given, check if current entry matches the condition, otherwise just update without regards for anything
                if num_of_conditions > 0:
                    conditions_matching = 0
                    
                    # Iterate through all conditions and check, wether current entry matches them
                    for cond in condition:
                        if condition[cond] == entry[cond]:
                            # If bool_op is AND, an entry must match all conditions, therefore just count the number of conds matching
                            if bool_op == 'AND':
                                conditions_matching += 1
                            elif bool_op == 'OR':
                                # otherwise just update, if one conditions matched and break afterwards
                                for key in mapping:
                                    entry[key] = mapping[key]
                                
                                num_of_entries_updated += 1
                                break
                    
                    # After all conditions have been checked, check if all conditions matched and update in that case
                    if bool_op == 'AND':
                        if conditions_matching == num_of_conditions:
                            for key in mapping:
                                entry[key] = mapping[key]
                            num_of_entries_updated += 1
                
                else:
                    # No conditions given, update fucking everything
                    for key in mapping:
                        entry[key] = mapping[key]
                    num_of_entries_updated += 1
        
        # Basically the exact same procedure as for lists, just with entries. I could put that whole block into a function but meh
        if entity == 'entry':
            for entry in self.entry:
                if num_of_conditions > 0:
                    conditions_matching = 0
                    
                    for cond in condition:
                        if condition[cond] == entry[cond]:
                            if bool_op == 'AND':
                                conditions_matching += 1
                            elif bool_op == 'OR':
                                for key in mapping:
                                    entry[key] = mapping[key]

                                num_of_entries_updated += 1
                                break
                    
                    if bool_op == 'AND':
                        if conditions_matching == num_of_conditions:
                            for key in mapping:
                                entry[key] = mapping[key]
                            num_of_entries_updated += 1
                
                else:
                    for key in mapping:
                        entry[key] = mapping[key]
                    num_of_entries_updated += 1
        
        # Write current db to file for persistence and return the number of updated entries
        self.write_db_to_file()
        return {'entries_updated': num_of_entries_updated}
    
    ###
    # @brief
    # deletes all entries that match the specified condition. For those entries, the properties will be set as defined in
    # the mapping parameter. If a property wasn't defined in mapping, it won't be changed
    # 
    # @param {String} entity: Entity from which all entries are to be retrieved. Mus be either 'list' or 'entry'
    # @param {Dictionary} mapping: Defines, how the matching entries should be deleted. Keys are properties to be upddeletedated, values are 
    #                               what is set. If a key is used, that isn't defined for that entity, an error is raised
    #                               Example:    {
    #                                               'name': 'New name that will be set for all entries that match the conditions'
    #                                           }
    # @param {Dictionary} condition (optioanl): Defines which entries should be deleted. Only entries having the properties defined in condition are deleted.
    #                                           Dictionary looks the same as in mapping.
    #                                           If no conditions are given, every single entry of given entity is deleted. Use with care.
    # @param {String} bool_op: Either 'AND' or 'OR'. If 'AND' is passed, entries must match ALL conditions. If 'OR' is passed, entries must only
    #                           match one condition
    # 
    # @return {Dictionary[]} All entries in the specified list
    ###
    def delete(self, entity=None, condition=None, bool_op='AND'):
        # Check if all entries are given and set correctly and raise lots of errors otherwise
        if not entity or entity == '':
            raise RuntimeError('No entity given.')
        
        if not (entity == 'list' or entity == 'entry'):
            raise ValueError('Type of entity not specified correctly.')
        
        if not bool_op or not (bool_op == 'OR' or bool_op == 'AND'):
            raise RuntimeError('bool_op must either be AND or OR.')
        
        if entity == 'list':
            if not not condition:
                for key in condition:
                    if not key in self.list_attributes:
                        raise ValueError('Lists do not have attribute ' + key)
        
        if entity == 'entry':
            if not not condition:
                for key in condition:
                    if not key in self.entry_attributes:
                        raise ValueError('Entries do not have attribute ' + key)

        # Get the number of conditions for future reference
        num_of_conditions = 0
        if not not condition:
            for key in condition:
                num_of_conditions += 1

        # deleted_entries is just for counting, current_index is to get the index of elements to be deleted
        deleted_entries = 0
        current_index = 0

        # List to save all entries to be deleted
        indices_to_delete = []

        # Iterate through all ist items and check, if they match the conditions. If they do. append their index to indices_to_delete
        if entity == 'list':
            for entry in self.list:
                conditions_matched = 0
                for cond in condition:
                    if entry[cond] == condition[cond]:
                        if bool_op == 'AND':
                            conditions_matched += 1
                        elif bool_op == 'OR':
                            indices_to_delete.append(current_index)
                            break
                
                if bool_op == 'AND' and num_of_conditions == conditions_matched:
                    indices_to_delete.append(current_index)
                
                current_index += 1

        # same as last comment
        if entity == 'entry':
            for entry in self.entry:
                conditions_matched = 0
                for cond in condition:
                    
                    if entry[cond] == condition[cond]:
                        if bool_op == 'AND':
                            conditions_matched += 1
                        elif bool_op == 'OR':
                            self.list.pop(current_index)
                            break
                
                if bool_op == 'AND' and num_of_conditions == conditions_matched:
                    indices_to_delete.append(current_index)
                
                current_index += 1

        # iterate through all indices_to_delete backwards and delete their entries
        for i in range(len(indices_to_delete)):
            if entity == 'entry':
                self.entry.pop(indices_to_delete[len(indices_to_delete) - 1 - i])
            elif entity == 'list':
                self.list.pop(indices_to_delete[len(indices_to_delete) - 1 - i])
            deleted_entries += 1
        
        self.write_db_to_file()
        return { 'deleted': deleted_entries}

    ###
    #
    # @brief
    # Deletes the entire database. Completely. Their won't be any way to retrieve it.
    #
    ###
    def drop(self):
        self.list = []
        self.entry = []
        self.write_db_to_file()

    def write_db_to_file(self):
        current_dir = os.getcwd()
        final_dir = os.path.join(current_dir, r'database')
        modifier = 'w'

        if not os.path.exists(final_dir + '\\db.json'):
            if not os.path.exists(final_dir):
                os.makedirs(final_dir)
            modifier = 'x'

        db_file = open(final_dir + '\\db.json', modifier)
        complete_db = {
            'list': self.list,
            'entry': self.entry
        }

        db_file.write('')

        db_file.write(json.dumps(complete_db))
        db_file.close()
        
        return