#connect order (socket() -> bind() -> listen() -> accept())
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
import socket
import select

HEADER_LENGTH = 10

IP = "0.0.0.0"    #using 0.0.0.0 means to listen on all available interfaces
PORT = 1234       #You can change any big numbers you like. However, 80 is an html page, so it cannot be done.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((IP, PORT))
s.listen()

# List of sockets for select.select()
sockets_list = [s]

clients = {}

print('Listening for connections on {}:{}...'.format(IP,PORT))


def receive_message(client_socket):
    try:     
        message_header = client_socket.recv(HEADER_LENGTH)
        #if no data was received ,close
        if not len(message_header):   
            return False
        #remove space in string
        message_length = int(message_header.decode('utf-8').strip())  
        return {'header': message_header, 'data': client_socket.recv(message_length)} 
    except:
        return False

def weather():
    try:        
        message_data = "We will search for u".encode('utf-8')
        message_length =b'20        '
      
        return {'header': message_length , 'data': (message_data)} 
    except:
        print("error")
        return False

def server_name():
    try:        
        name_data ="server".encode('utf-8')
        name_length = b'6         '
     
        return {'header': name_length , 'data': (name_data)} 
    except:
        print("error")
        return False
    

while True:  
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    for lis in read_sockets:
        # If a new connection, accept it
        if lis == s:
            #Accept new connection
            client_socket, client_address = s.accept() 
            #recceive client name
            user = receive_message(client_socket)  
            # If client disconnected before he sent his name
            if user is False:    
                continue
            #add client_socket to  sockets_list
            sockets_list.append(client_socket)           
            #save username and username header
            clients[client_socket] = user    
            print('Accepted new connection from {}:{}, username-> {}'.format(*client_address, user['data'].decode('utf-8')))


        # If already existing socket is sending a message
        else:
            # Receive message
            message = receive_message(lis)
           

            # If client disconnected,cleanup
            if message is False:
                print('Closed connection from: {}'.format(clients[lis]['data'].decode('utf-8')))
                # Remove from list for socket.socket()
                sockets_list.remove(lis)
                # Remove from our list of users
                del clients[lis]
                continue


          
            # Get user by notified socket, so we will know who sent the message
            user = clients[lis]
            print('Received message from {}: {}'.format(user["data"].decode("utf-8") ,message["data"].decode("utf-8")))

            if message['data'] != b'quite':
                if message['data']==b'weather':
                    for client_socket in clients:
                        if client_socket == lis:
                            reply=weather()
                            name=server_name()
                            #print("{} {}".format(reply['header'],reply['data']))
                            #print("{} {}".format(name['header'],name['data']))
                            client_socket.send(name['header'] + name['data'] + reply['header'] + reply['data'])
                            print("{} {} {} {} ".format(name['header'],name['data'],reply['header'],reply['data']))
              

            #broadcast message over connected clients
            for client_socket in clients:
                # message will send  to all client expect sender
                if client_socket != lis:                    
                    #message header sent by sender, and saved username header send by user when he connected
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
                    print("{} {} {} {} ".format(user['header'],user['data'],message['header'],message['data']))
                    
