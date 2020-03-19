import logging
import sys


'''
exit 1 : db type error
exit 2 : option error
exit 3 : file read end 


'''


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import getopt
import shutil
import os
import time
from datetime import datetime


'''
set env
'''

bool = True
while bool:
    try:
        import cx_Oracle
        bool = False
    except ImportError:
        os.popen('python -m pip install cx_Oracle --upgrade')

if os.name != 'nt':
    hostname = os.uname()[1]
    ip = os.popen("ip a | grep ens33 | grep inet | awk -F' ' '{print $2}' | awk -F/ '{print $1}'").read()
    path = os.environ['PWD']

'''

'''

class InitDBConnecter(object):

    _type = ['mysql','oracle','redis']

    def initOracle(self, *args,**kwargs):
        try:
            db = cx_Oracle.connect(kwargs['user'],kwargs['passwd'],\
                               '{0}:{1}/ORCL'.format(kwargs['host'],kwargs['port']), encoding="UTF-8")
        except cx_Oracle.DatabaseError:
            os.popen('rpm -ivh ./packages/oracle-instantclient19.3-basic-19.3.0.0.0-1.x86_64.rpm')
        else:
            return db

    def initMysql(self):
        pass

    def initRedis(self):
        pass

    def __call__(self, *args, **kwargs):
        #check db type,
        if kwargs['type'] not in InitDBConnecter._type:
            logging.info('db type error')
            sys.exit(1)

        if kwargs['type'] == 'oracle':
            return self.initOracle(user=kwargs['user'],passwd=kwargs['passwd'],host=kwargs['host'],port=1521)


class GetMetre(object):

    def __init__(self,db=None):
        self.db = db
        self.cursor = db.cursor()

        process = self.getprocess()
        client = self.getclient()
        with open('result.pkl','wa') as self.f:
            self.f.write(hostname+' process '+str(process[0])+' '+str(time.time())+'\n')
            self.f.write(hostname+' processCount '+str(client[2])+' '+str(time.time())+'\n')

            Sender(host=hostname, key='process',value=process[0])
            Sender(host=hostname, key='processCount',value=client[2])


    def getclient(self):
        '''
        get client messages
        :return:
        '''
        sql = '''select event,sql_id,count(*) from gv$session where \
        wait_class<>'Idle' group by event,sql_id order by 3 desc'''
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        return row

    def getprocess(self):
        '''
        get db process
        :return:
        '''
        sql = '''select count(*) from gv$process'''
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        return row

    def close(self):
        self.db.close()

class Sender(object):

    def __init__(self,host,key,value):
        os.popen('zabbix_sender -z 192.168.32.241 -s {0} -k {1} -o {2}'.format(host, key, value))


    def move(self):
        if os.path.getsize('result.pkl') > 311:
            with open('./bak/backup.log','wb') as f:
                f.write(str(datetime.now())+' STARING BACKUPS .... ....\n')

            shutil.move('result.pkl','./bak/result-{}.pkl'.format(time.time()))

            os.environ['TIMESTAMPE'] = str(0)


if __name__ == '__main__':

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h:u:p:t:',['help'])
        hostinfo = dict(opts)
        if len(opts) == 0:
            raise getopt.GetoptError(None)

        if '--help' in hostinfo.keys():
            print 'Usages:python oracle.py -h ? -t ? ... \n\tpython oracle.py --help ,see help\n'
            print '-h       set host ip\n-p       set passwd\n-u       set user\n-t       set db type'
            sys.exit(2)

        host, user, passwd, type = hostinfo['-h'],hostinfo['-u'],hostinfo['-p'],hostinfo['-t']
        db = InitDBConnecter()
        conn = db(host=host, user=user, passwd=passwd,type=type)

        g = GetMetre(db=conn)
        g.close()
    except getopt.GetoptError as e:
        logging.info('No args or invild options,Please use --help ,see usage')


