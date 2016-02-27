from panda3d.core import *
from pandac.PandaModules import *
from direct.task.TaskManagerGlobal import *
from direct.task.Task import Task
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from src.util.types import *
import threading

class ClientAgent(QueuedConnectionManager):
    
    def __init__(self, server_address, server_port, client_address, client_port):
        QueuedConnectionManager.__init__(self)
        self.server_address = server_address
        self.server_port = server_port
        self.client_address = client_address
        self.client_port = client_port

        # Keep track of how recently we last sent a heartbeat message.
        # We want to keep these coming at heartbeatInterval seconds.
        self.heartbeat_interval = base.config.GetDouble('heartbeat-interval', 15)
        self.new_heartbeat = None
        self.last_heartbeat = None
    
    def configure(self):
        self.cl = QueuedConnectionListener(self, 0)
        self.cr = QueuedConnectionReader(self, 0)
        self.cr2 = QueuedConnectionReader(self, 0)
        self.cw = ConnectionWriter(self, 0)
        self.our_channel = CLIENT_AGENT_CHANNEL
        self.allocated_channels = 0
        self.connection_list = []
        self.connection_to_channel = {}
        self.open_connection()
        self.run_connection()
    
    def unconfigure(self):
        for participant in self.interface:
            self.cr.removeConnection(participant)
        self.closeConnection(self.tcp_socket)
        self.closeConnection(self.tcp_conn)
        self.cl = self.cr = self.cw = self.tcp_socket = self.tcp_conn = None

    def register_for_channel(self, channel):
        datagram = PyDatagram()
        datagram.addServerHeader(channel, channel, CONTROL_SET_CHANNEL)
        self.cw.send(datagram, self.tcp_conn)
	
    def unregister_for_channel(self, channel):
        datagram = PyDatagram()
        datagram.addServerHeader(channel, channel, CONTROL_REMOVE_CHANNEL)
        self.cw.send(datagram, self.tcp_conn)

    """ TODO: Work in progress got lazy didn't finish, too much work for now... """
    def allocate_new_channel(self): # TODO: when client disconnects, remove its channel and reset the id values.
        self.channel_allocated = UniqueIdAllocator(1100, 1500).allocate()
        if self.channel_allocated > 1000000000:
            return Exception("Already generated the max number of channels!")

        self.allocated_channels = self.allocated_channels + self.channel_allocated
        return int(self.channel_allocated) 

    def setup_new_connection_channel(self, connection):
        new_client_channel = self.allocate_new_channel()
        self.connection_to_channel[connection] = new_client_channel
        self.register_for_channel(new_client_channel)

    def open_connection(self):
        self.tcp_socket = self.openTCPServerRendezvous(self.server_port, 1000)
        if self.tcp_socket:
            self.cl.addConnection(self.tcp_socket)
            
            taskMgr.add(self.task_listner_poll, "task listner")
            taskMgr.add(self.task_reader_poll, "task reader")
    
    def run_connection(self):
        self.tcp_conn = self.openTCPClientConnection(self.client_address, self.client_port, 3000)
        if self.tcp_conn:
			self.register_for_channel(self.our_channel)
			self.cr2.addConnection(self.tcp_conn)

			taskMgr.add(self.task_reader_poll_reciever, "task reader reciever")
    
    def task_listner_poll(self, taskname):
        if self.cl.newConnectionAvailable():
            rendezvous = PointerToConnection()
            netAddress = NetAddress()
            newConnection = PointerToConnection()
            
            if self.cl.getNewConnection(rendezvous, netAddress, newConnection):
                newConnection = newConnection.p()
                self.connection_list.append(newConnection)
                self.setup_new_connection_channel(newConnection)
                self.cr.addConnection(newConnection)
        
        return Task.cont
    
    def task_reader_poll(self, taskname):
        if self.cr.dataAvailable():
            datagram = NetDatagram()
            if self.cr.getData(datagram):
                self.handle_datagram(datagram)
        
        return Task.cont
    
    def close_connection(self, code, reason, connection):
        datagram = PyDatagram()
        datagram.addUint16(CLIENT_GO_GET_LOST)
        datagram.addUint16(int(code))
        datagram.addString(str(reason))
        self.cw.send(datagram, connection)
        self.remove_connection_instance(connection)

    def handle_datagram(self, datagram):
        self.connection = datagram.getConnection()
        if not self.connection:
            pass # TODO!
        
        di = PyDatagramIterator(datagram)
        msg_type = di.getUint16()
        print msg_type # debug
        
        if msg_type == CLIENT_HEARTBEAT:
            self.handle_client_heartbeat(self.connection, di)
        elif msg_type == CLIENT_DISCONNECT:
            self.remove_connection_instance(self.connection)
        else:
            print ("Recieved an unexpected datagram: %s from: %s" % (msg_type, str(self.connection)))
	
    def handle_client_heartbeat(self, connection, di):
		try:
			taskMgr.remove(self.new_heartbeat)
			self.last_heartbeat = self.new_heartbeat
		except:
			self.last_heartbeat = None
			self.new_heartbeat = None
		
		self.new_heartbeat = taskMgr.doMethodLater(self.heartbeat_interval, self.handle_heartbeat_ended, "heartbeat stopped", extraArgs=[connection])
       
    def handle_heartbeat_ended(self, taskname):
		self.close_connection(code=122, reason="The client hasn't responded with a heartbeat within the past 15 seconds!",
								connection=self.connection) # huh, for some reason i can't use extraArgs?

    """ This task handles incoming data for the clientagent """
    def task_reader_poll_reciever(self, taskname):
        if self.cr2.dataAvailable():
            datagram = NetDatagram()
			
            if self.cr2.getData(datagram):
                self.handle_datagram_reciever(datagram)

        return Task.cont

    """ Gotta run this by the MD when the connection is stored in the MD's participant interface."""
    def remove_connection_instance(self, connection):
        if connection in self.connection_list:
            self.cr.removeConnection(connection)
            self.connection_list.remove(connection)

        return


    def handle_datagram_reciever(self, datagram):
        connection = datagram.getConnection()
        if not connection:
            print ("Got an unexpected connection: %s" % str(connection))
            return
        
        di = PyDatagramIterator(datagram)
        reciever_channel = di.getUint64()
        sender_channel = di.getUint64()
        msg_type = di.getUint16()
        print msg_type
