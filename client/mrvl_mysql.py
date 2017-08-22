import time
import string
import os
import MySQLdb
import threading

class mrvl_mysql:  
    """
    The constructor
    """
    def __init__(self, logger, db_name, hostname='localhost', username='root', password='123456'):
        self.main_logger = logger
        self.lock = threading.Lock()
        try:
            self.conn=MySQLdb.connect(host=hostname,user=username,passwd=password,db=db_name)
            self.cur=self.conn.cursor()
        except MySQLdb.Error,e:
            self.main_logger.error( "MySql Error! %s"%str(e))


    def __readsql_cmd(self, cmd):
        ret = False
        self.lock.acquire()
        try:
            self.main_logger.info('read cmd from mysql:%s'%cmd)
            self.conn.commit()
            self.cur.execute(cmd)
            results = self.cur.fetchall()
            #self.main_logger.info('get data from mysql:%s'%str(results))
            ret = True
        except MySQLdb.Error, e:
            results = "Get exception:%s when read mysql:%s"%(str(e), cmd)
            self.main_logger.error( results)
        except Exception,e:
            results = "Get exception:%s when read mysql:%s"%(str(e), cmd)
            self.main_logger.error( results)
        except:
            results = "Get exception:%s when read mysql:%s"%('unknown', cmd)
            self.main_logger.error( results)
        self.lock.release()
        return ret, results

    def __writesql_cmd(self, cmd):
        ret = False
        self.lock.acquire()
        try:
            self.main_logger.info('write cmd into mysql:%s'%cmd)
            self.cur.execute(cmd)
            self.conn.commit()
            ret = True
        except MySQLdb.Error, e:
            results = "Get exception:%s when write mysql:%s"%(str(e), cmd)
            self.main_logger.error( results)
        except Exception,e:
            results = "Get exception:%s when write mysql:%s"%(str(e), cmd)
            self.main_logger.error( results)
        except:
            results = "Get exception:%s when write mysql:%s"%('unknown', cmd)
            self.main_logger.error( results)

        self.lock.release()
        return ret

    def __chk_args(self, table_name, args):
        keys = self.select_keys(table_name)
        keys_from_args = args.keys()
        for key in keys_from_args:
            if key not in keys:
                return False
        return True


    def select_keys(self, table_name):
        cmd = 'show columns from %s'%table_name
        ret, results = self.__readsql_cmd(cmd)
        if not ret:
            return []
        keys = []
        for r in results:
            keys.append(str(r[0]))
        return keys

    def select_table(self, table_name, args_where=None, keys=None, orderby=None):
        if orderby == None:
            order_by_str = ''
        else:
            order_by_str = 'order by %s'%orderby
        if keys == None:
            keys_str = '*'
        else:
            keys_str = ','.join(keys)
        if args_where==None or len(args_where.keys()) == 0:
            where_str = ''
        else:
            where_str = 'where '
            for key in args_where.keys():
                where_str += '%s=\'%s\' and '%(key, args_where[key])
            where_str = where_str[:-5]
        cmd = 'select %s from %s %s %s'%(keys_str, table_name, where_str, order_by_str)
        ret, results = self.__readsql_cmd(cmd)
        if keys != None and 'id' in keys:
            self.main_logger.trace('Send mysql command:%s'%cmd)
        table_data = []
        if not ret:
            return []
        return results

    def insert(self, table_name, args):
        table_keys = self.select_keys(table_name)
        table_keys.sort()
        args_keys = args.keys()
        args_keys.sort()
        if args != None:# and table_keys == args_keys:
            values_str = ''
            keys_str = ''
            for key in args_keys:
                values_str += '\'%s\','%args[key]
                keys_str += key + ','
            cmd = 'insert %s (%s) values (%s)'%(table_name, keys_str[:-1], values_str[:-1])
            self.main_logger.info( cmd)
            return self.__writesql_cmd(cmd)
        else:
            return False 
        pass
    def update(self, table_name, args_update, args_where):
        if args_where == None or len(args_where.keys()) == 0:
            return self.insert(table_name, args_update)
        result = self.select_table(table_name, args_where)
        if len(result) == 0:
            for key in args_where.keys():
                if not args_update.has_key(key):
                    args_update[key] = args_where[key]
            return self.insert(table_name, args_update)
        update_str = ''
        for key in args_update.keys():
            update_str += '%s=\'%s\','%(key, args_update[key])
        update_str=update_str[:-1]
        where_str = ''
        for key in args_where.keys():
            where_str += '%s=\'%s\' and '%(key, args_where[key])
        where_str = where_str[:-5]
        cmd = 'update %s set %s where %s'%(table_name, update_str, where_str)
        self.main_logger.info( cmd)
        return self.__writesql_cmd(cmd)
        
    def delete(self, table_name, args):
        if len(args.keys()) > 0 and self.__chk_args(table_name, args):
            cmd = 'delete from %s where '%table_name
            for key in args.keys():
                cmd += '%s=\'%s\' and '%(key, args[key])
            self.main_logger.info( cmd[:-5])
            return self.__writesql_cmd(cmd[:-5])
                
        return False
    def insert_and_update(self, table_name, args):

        pass



    """
    The destructor
    """
    def __del__(self):
        del self.lock


if __name__ == '__main__':
    test_hdlr = mrvl_mysql(None, 'Case_Dispatcher')
##    keys=test_hdlr.select_keys('test_result')        
##    print keys
    start = time.time()
    data = test_hdlr.select_table('test_result')
    print data
    print (time.time() - start)

