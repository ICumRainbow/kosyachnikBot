UPDATE_USER_ROW_QUERY = "UPDATE users SET username=%s, name=%s WHERE id=%s"
SELECT_LAST_WINNER_QUERY = 'SELECT users.username AS "winner_username", users.name AS "winner_name", users.id AS "id" ' \
                       'FROM contest_groups ' \
                       'JOIN users ON contest_groups.id=%s AND contest_groups.winner_id=users.id;'
SELECT_LAST_TIME_QUERY = 'SELECT CONVERT_TZ(last_time,"-04:00", "+05:00") AS "last_time" FROM contest_groups WHERE id=%s'
UPDATE_LAST_TIME_QUERY = "UPDATE contest_groups SET last_time=%s, winner_id=%s WHERE id=%s"
SELECT_LAST_TIME_NOT_NULL_QUERY = 'SELECT last_time FROM contest_groups WHERE id=%s and last_time IS NOT NULL'
UPDATE_SCORE_QUERY = 'UPDATE scores SET score = score + 1 WHERE chat_id = %s AND user_id =%s'
SELECT_CHAT_ID_QUERY = 'SELECT chat_id FROM scores WHERE chat_id=%s'
SELECT_USER_QUERY = 'SELECT username, name from users WHERE id=%s'
SELECT_FETCH_STATS_QUERY = '''SELECT users.username AS "username", users.name AS "name", users.id AS "id", scores.score as "score" 
                              FROM scores JOIN users 
                                   ON scores.user_id=users.id 
                              WHERE scores.chat_id=%s 
                              ORDER BY scores.score DESC;'''
SELECT_STATS_QUERY = '''SELECT IFNULL(users.username, users.name) AS "name" 
                   FROM scores 
                   JOIN users ON scores.chat_id=%s AND scores.user_id=users.id;'''

SELECT_ID_QUERY = "SELECT id from users where id=%s"
INSERT_USER_QUERY = "INSERT INTO users VALUES(%s,%s,%s)"
SELECT_GROUP_QUERY = "SELECT id from contest_groups where id=%s"
INSERT_GROUP_QUERY = "INSERT INTO contest_groups(id) VALUES(%s)"
INSERT_SCORE_QUERY = "INSERT INTO scores(chat_id,user_id) VALUES(%s,%s)"
SELECT_USER_ID_QUERY = 'select user_id from scores where chat_id=%s and user_id=%s'
