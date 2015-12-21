# Testing purposes only!
from src.messagedirector.MessageDirector import MessageDirector
from src.clientagent.ClientAgent import ClientAgent
from direct.showbase.ShowBase import ShowBase
showbase = ShowBase()
md = MessageDirector('localhost', 7101)
md.configure()

ca = ClientAgent('localhost', 7102, 'localhost', 7101)
ca.configure()

showbase.run()
