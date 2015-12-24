# Testing purposes only!
from pandac.PandaModules import loadPrcFileData
loadPrcFileData("", "window-type none")

from src.messagedirector.MessageDirector import MessageDirector
from src.clientagent.ClientAgent import ClientAgent
from src.stateserver.StateServer import StateServer
from direct.showbase.ShowBase import ShowBase
showbase = ShowBase()

md = MessageDirector('127.0.0.1', 7101)
md.configure()

ca = ClientAgent('127.0.0.1', 7102, '127.0.0.1', 7101)
ca.configure()

ss = StateServer('127.0.0.1', 7101)
ss.configure()

showbase.run()
