import pymysql
"""
测试的时候由于使用批量导入sql出现问题，则使用这样的单条插入数据库的脚本运行
（mysql -h数据库ip地址 -u数据库用户名 -p数据库密码 数据库 < areas.sql）没倒进来
下下策才使用，如果数据量很大那就使用多进程多线程
"""
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="mysql",
    database="meiduo",
    charset='utf8')

cursor = conn.cursor()

with open('areas.sql', 'r', encoding='utf8') as f:
    while True:
        line = f.readline()

        if line:
            print(line)
            cursor.execute(line)
            conn.commit()
        else:
            break

cursor.close()

conn.close()