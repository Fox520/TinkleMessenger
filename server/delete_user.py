import dataset,os.path

database_name = raw_input("Enter database name: ")
if os.path.isfile(database_name):
    table_to_use = raw_input("Enter table name: ")
    db = dataset.connect('sqlite:///'+database_name)
    table = db[table_to_use]
    name_to_remove = raw_input("Enter name to remove: ")
    try:
        a = db[table_to_use].find_one(name=name_to_remove)
        if a != None:
            table.delete(name=name_to_remove)
            print name_to_remove,"has been removed"
        else:
            print name_to_remove,"not found"
    except Exception as e:
        print e
        print "User not found"