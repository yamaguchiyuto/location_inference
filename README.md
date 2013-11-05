location_inference
==================

Location inference methods

Run 'python evaluation.py' for help.

# Data to prepare

## users.json

{"location_point": ["latitude", "longitude"], "id": "user id"}  
.  
.  
.  

## graph.json

{"src_id": "source user id", "dst_ids": ["destination user id", "destination user id", ...]}  
.  
.  
.  

# DB to prepare

## tweet table  
+-----------+------------+------+-----+---------+-------+  
| Field     | Type       | Null | Key | Default | Extra |  
+-----------+------------+------+-----+---------+-------+  
| id        | bigint(20) | NO   | PRI | 0       |       |  
| text      | text       | YES  |     | NULL    |       |  
| timestamp | datetime   | YES  | MUL | NULL    |       |  
| user_id   | bigint(20) | YES  | MUL | NULL    |       |  
+-----------+------------+------+-----+---------+-------+  


