# Manager script

# Communication between computers will be done through MQTT
# The allows easy 2 way communication will multiple devices



# objects to be used in the database
# PC Management
class Computer:
    def __init__(self, name, address):
        self.name = name
        self.address = address
        
    def launch(self, game, options = None):
        # setup client first before doing too much
        pass

    # todo: setup actions

class Group:
    def __init__(self, name, computers):
        self.name = name
        self.computers = computers
    
    def launch(self, game, options = None):
        # setup client first before doing too much
        for computer in self.computers:
            computer.launch(game, options)

    # todo: setup actions
    
class Arragement:
    def __init__(self, name, groups): # for higher level grouping, can include arragemnts aswell
        self.name = name
        self.groups = groups
    def launch(self, game, options = None):
        # setup client first before doing too much
        for group in self.groups:
            group.launch(game, options)
        pass
    
    # todo: setup actions




# Communication functions
def main():
    # Manage the health of the different management functions
    pass



