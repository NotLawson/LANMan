# objects to be used in the database

# PC Management
class Computer:
    def __init__(self, name, address):
        self.name = name
        self.address = address
    # todo: setup actions

class Group:
    def __init__(self, name, computers):
        self.name = name
        self.computers = computers
    # todo: setup actions
    
class Arragement:
    def __init__(self, name, groups): # for higher level grouping, can include arragemnts aswell
        self.name = name
        self.groups = groups
    # todo: setup actions

