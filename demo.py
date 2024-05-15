import datetime

from wxauto import WeChat
import time
import psycopg2

# 实例化微信对象
wx = WeChat()

# 指定监听目标（只包括群组）
listen_list = [
    '测试群1',
    '测试群2'
]

# 添加监听对象
for i in listen_list:
    wx.AddListenChat(who=i, savepic=False)  # 添加监听对象，不自动保存新消息图片

# 设置监控关键字
keywords = ['项目进度', '会议']

# 连接到pgsql数据库，如果不存在则创建    需要创建个数据库 --testdb
conn = psycopg2.connect(database="testdb", user="postgres", password="313131", host="127.0.0.1", port="5432")
cursor = conn.cursor()

# 创建一个新表来存储消息
cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    group_name TEXT,
    sender_name TEXT,
    message TEXT,
    time TEXT
)
''')
conn.commit()

# 持续监听消息
wait = 10  # 设置10秒查看一次是否有新消息
while True:
    msgs = wx.GetListenMessage()
    for chat in msgs:
        one_msgs = msgs.get(chat)  # 获取消息内容
        for msg in one_msgs:
            print(msg.__dict__)
            if any(keyword in msg.content for keyword in keywords):
                # 如果消息内容包含任何一个关键字，插入数据库
                # 检查chat对象是否与监听列表中的群名相匹配，并将群名作为sender
                groupName = next((group for group in listen_list if group in str(chat)), 'Unknown')
                cursor.execute('INSERT INTO messages (group_name, sender_name, message, time) VALUES (%s, %s, %s, %s)',
                           (groupName, msg.sender, msg.content, datetime.datetime.now()))
            conn.commit()

        time.sleep(wait)

# 关闭数据库连接
conn.close()
