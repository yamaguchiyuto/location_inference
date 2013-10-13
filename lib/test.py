from db import DB

db = DB('yuto', 'sinpai56you', 'kdecamp2013')

result = db.issue_select('select * from users')

for row in result:
    print "%s,%s" % (row['id'], row['location'])
