from datetime import datetime
from key_generator.key_generator import generate
import sys

def keygen(numseed):
    curdate = datetime.now()
    dmy = curdate.day+curdate.month+curdate.year
    time = curdate.hour+curdate.minute
    timeseed = dmy+time
    key = generate(num_of_atom=1, separator='', min_atom_len=24, max_atom_len=24, type_of_value='hex', capital='mix', extras=['!','@','#','%','^','&','*','_','-','+','?'], seed=numseed+timeseed).get_key()
    return key

numseed = int(sys.argv[1])
key = keygen(numseed)
print(key)