import dataset,os.path

database_name = input("Enter database name: ")
if os.path.isfile(database_name):
    table_to_use = input("Enter table name: ")
    db = dataset.connect('sqlite:///'+database_name)
    table = db[table_to_use]
    name_to_remove = input("Enter name to remove: ")
    try:
        a = db[table_to_use].find_one(name=name_to_remove)
        if a != None:
            table.delete(name=name_to_remove)
            print(name_to_remove,"has been removed")
        else:
            print(name_to_remove,"not found")
    except Exception as e:
        print(e)
        print("User not found")