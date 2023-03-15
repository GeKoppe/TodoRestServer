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
            db_file = open(final_dir + '\\db.json', 'r')
            db_json = json.loads(db_file.read())
            self.list = db_json['list']
            self.entry = db_json['entry']
        
    

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
                self.entry.append(dict_to_push)

            if entity == 'list':
                entries_written += 1
                self.list.append(dict_to_push)

        return { 'written': entries_written, 'total': total_entries }
    

    def select_all (self, entity=None):
        if not entity or entity == '':
            raise ValueError('No entity given')

        if entity == 'list':
            return self.list
        elif entity == 'entry':
            return self.entry
        
        return []

    def update(self, entity=None, mapping=None, condition=None, bool_op='AND'):
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
        
        num_of_conditions = 0
        if not not condition:
            for key in condition:
                num_of_conditions += 1

        num_of_entries_updated = 0
        if entity == 'list':
            for entry in self.list:
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

        return {'entries_updated': num_of_entries_updated}
    

    def delete(self, entity=None, condition=None, bool_op='AND'):
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
                    
        num_of_conditions = 0
        if not not condition:
            for key in condition:
                num_of_conditions += 1

        deleted_entries = 0
        current_index = 0
        if entity == 'list':
            for entry in self.list:
                deleted = False
                conditions_matched = 0
                for cond in condition:
                    
                    if entry[cond] == condition[cond]:
                        if bool_op == 'AND':
                            conditions_matched += 1
                        elif bool_op == 'OR':
                            self.list.pop(current_index)
                            
                            deleted = True
                            break
                
                if bool_op == 'AND' and num_of_conditions == conditions_matched:
                    self.list.pop(current_index)
                    deleted = True
                
                if not deleted:
                    current_index += 1

        if entity == 'entry':
            for entry in self.entry:
                deleted = False
                conditions_matched = 0
                for cond in condition:
                    
                    if entry[cond] == condition[cond]:
                        if bool_op == 'AND':
                            conditions_matched += 1
                        elif bool_op == 'OR':
                            self.list.pop(current_index)
                            
                            deleted = True
                            break
                
                if bool_op == 'AND' and num_of_conditions == conditions_matched:
                    self.list.pop(current_index)
                    deleted = True
                
                if not deleted:
                    current_index += 1

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
            

                    