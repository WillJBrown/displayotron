from mypylib import portainer
import dothat.touch as nav
from dot3k.menu import Menu, MenuOption
from collections import OrderedDict
import pprint

import threading

class Docker(MenuOption):

    def __init__(self, lcd, idle_handler, idle_timeout, input_handler):
        self.status = {}
        self.endpoints = []
        self.containers = []
        self.stacks = []
        self.structure = {
#               'Status': {},
            'Stacks': List(self.stacks),
            'Containers': List(self.containers),
            'Endpoints': List(self.endpoints)
        }

        self.last_update = self.millis()
        self.updating = False
        SubMenu.__init__(self, self.structure, lcd, idle_handler, idle_timeout, input_handler)


    def begin(self):
        self.update(True)

    def update(self, force=False):
        # Update only once every 30 seconds
        if self.millis() - self.last_update < 1000 * 30 and not force:
            return False

        self.last_update = self.millis()

        update = threading.Thread(None, self.do_update)
        update.daemon = True
        update.start()


    def do_update(self):
        if self.updating:
            return False

        self.updating = True

#        print("doing update")

#        self.status = {}
        self.endpoints = []
        self.containers = []
        self.stacks = []

        self.status = portainer.getstatus()
        for ename, endpoint in self.status.items():
            self.endpoints.append(ename)
            for cname, container in endpoint['Containers'].items():
                self.containers.append(cname)
        self.stacks = list(portainer.liststacks().keys())

        self.updatemenu(self.structure)

#        print("update done")
#        print(len(self.containers))
#        pprint.pprint(self.containers)


        self.updating = False


    def redraw(self, menu):
        self.update()
        now = self.millis()
        if now - self.last < 1000:
            return False
        self.last = now
        Menu.redraw(self)

class List(MenuOption):

    def __init__(self, flat_string_list):
        self.last = self.millis()
        self.list = flat_string_list
        self.index = 0
        self.length = len(self.list)
        MenuOption.__init__(self)

    def updatelist(self, newlist):
        self.list = newlist
        self.length = len(self.list)
        self.index = min(self.index, self.length - 1)

    def up(self):
        self.index = (self.index-1)%self.length
        return True

    def down(self):
        self.index = (self.index+1)%self.length
        return True

    def redraw(self, menu):
        now = self.millis()
        if now - self.last < 1000:
            return False
        self.last = now

        for i in range(3):
            if self.length > i:
                line = self.list[(self.index + i) % self.length]
                menu.write_option(
                    row = i,
                    icon = (chr(252) if i == 0 else ' '),
                    text = line,
                    margin = 1,
                    scroll = ( len(line) > 15 )
                    )
            elif i == 0:
                menu.write_row(0, 'No Entries')
            else:
                menu.clear_row(i)



