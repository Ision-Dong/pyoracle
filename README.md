# pyoracle
For get oracle monitor metre to zabbix server
Usage:
  you can use python ./oracle.py --help ,see how to use it.
  
  Running environment：
          python2.7
          install cx_Oracle
          install oracle-instantclient19.3
  
  
  Now ,I only do Oracle monitoring,and There are many bugs to fix.
  
  Some extensions are reserved.
  
          GetMetre object can add functions to get monitor metre.
          InitDBConnecter object can add init db connect.
          
          
  Example:
          python oracle.py -h <oracle ip> -u <user> -p <passwd> -t <db type>
  
  
