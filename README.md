The py-OTP project is now RealTime-OTP

# RealTime-OTP
* RealTime-OTP is a re-implementation of Disney's OTP server, targeted for multiplayer games, and written in c/c++ and/or python.
* RealTime-OTP is open-source and is free to use.

# MessageDirector:
* The MessageDirector is perhapse the most important key component of the server, this server manages connections and their channels. 
* Registering channels: When a process connects to the MessageDirector and requests a register of it's channel, the MessageDirector will verify its connection and register its channel. 
* Routing messages: When a process wants to send some data from its process to another process it will send in a message to the MessageDirector with a value of its channel this is known as a sender, the other value will be the reciever/target channel.

# ClientAgent:
* This process handles connections between the clients and the RT-OTP cluster. 
* Security is key here, NEVER TRUST THE CLIENT! 
* When a new client connects and wants to send a message such as heartbeat or addInterest we need to verify that clients request, we must make sure such request is not something that is gonna harm us in any way. 
* Every connection in the cluster has to have a registered channel, therefore we must allocate a channel for the clients to operate on if their connected to the cluster.

# StateServer:
* The StateServer is also a very important part of the cluster, this server manages distributed objects and their interest, state. 
* Object generation: When an object is generated, the StateServer creates a server side instance of that object and stores it away for later use. 
* Updating objects: If the object needs a field update or location update. 
* the StateServer will perform either on the object. Disable objects: If the object is located on the StateServer and the client requests to delete it's object or the client disconnects the StateServer will remove that instance from its many do's.

# EventLogger:
* The EventLogger logs certain interesting events, the event logger does not log everything!
* Lets take toontown for example, if an avatar sends a field update for an unknown object or an invalid field, the event logger will log that event.
