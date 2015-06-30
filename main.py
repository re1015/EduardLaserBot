import time
import praw
import sqlite3
import sys
import pprint
# make sure you actually installed those libraries..

def check_keyword(keywords, comment):
	for kw in keywords:
		if kw in comment:
			return kw
	return false

def main():
	print("Welcome to EduardLaserBot v0.2!")
	### setting up username and stuff, you should probably not use your 'real' reddit account for a bot on Reddit ###
	db = "eduard.db" 
	user = input("Please enter your Username: ")
	pw = input("Please enter your Password: ")
	sub = input("Please enter the desired Subreddit: ")
	# setting up User Agent
	r = praw.Reddit('Eduard Laser Parser by u/Ekrow v0.2'
					'Url: http://www.ekrow.de')
	r.login(user, pw)
	subreddit = r.get_subreddit(sub)
	bot = r.get_redditor(user)

	### the keywords which the bot reacts to and their given replies and a footer text. There is probably a better way but I suck at Python ###
	keywords = ['Lauchboy', "Nebel", "Nilsoff", "Laserdojo", "Laserschelle", "Laserkick", "Laserstern", "Laserschellen", "Laserkicks", "Freiheit", "Eduard Laser", "Unmöglich"]
	replies = {
				"Freiheit": "Freiheit ist mir wichtig!", 
				"Lauchboy" : "Was redest du über meinen Sohn? Willste 'ne Laserschelle, oder was?", 
				"Nebel" : "Nebelflüssigkeit bekommt wenn man Nebel ganz hart schlägt", 
				"Nilshoff" : "Dieser Schurke macht Schurkensachen!",
				"Laserdojo" : "Das einzig wahre Laserdojo!",
				"Laserschelle" : "Laserschelle!",
				"Laserschellen" : "Laserschelle!",
				"Laserkick" : "Laserkick!",
				"Laserkicks" : "Laserkick!",
				"Laserstern" : "Laserstern!",
				"Eduard Laser" : "Für dich immer noch Eduard 'Unmöglich' Laser!",
				"Unmöglich" : "Unmöglich ist mein zweiter Name!"
		}
	footer_txt = "\n \n [Source](https://github.com/Ekrow/EduardLaserBot/)" 

	already_done = set()
	submission_already_done = set()
	### setting up the sqlite database to store already parsed comments and OP texts (We don't want to spam, right?)
	connection = sqlite3.connect(db)
	cursor = connection.cursor()
	cursor.execute("""CREATE TABLE IF NOT EXISTS parsed(id INTEGER PRIMARY KEY NOT NULL, comment_id VARCHAR(20));""")
	cursor.execute("""CREATE TABLE IF NOT EXISTS parsed_submission(id INTEGER PRIMARY KEY NOT NULL, submission_id VARCHAR(20));""")
	cursor.execute("SELECT * FROM parsed")
	result = cursor.fetchall()
	for res in result:
		already_done.add(res[1])
	cursor.execute("SELECT * FROM parsed_submission")
	result_submission = cursor.fetchall()
	for res_submission in result_submission:
		submission_already_done.add(res_submission[1])

	cnt = 0

	print("All set. Ready to parse")
	while True:
		for submission in subreddit.get_hot(limit=50):
			try:
				print("Checking Submission:" + submission.title + "(" + submission.id + ")")
				op_text = submission.selftext
				op_has_keyword = any(string in op_text for string in keywords)
				if submission.id not in submission_already_done and op_has_keyword:
					submission.add_comment('Freiheit ist dem OP wichtig' + footer_txt)
					print("Matched keyword in OP")
					cursor.execute("""INSERT INTO parsed_submission (id, submission_id) VALUES (NULL, ?);""", [submission.id])
					submission_already_done.add(submission.id)
					connection.commit()
					cnt += 1
				flat_comments = praw.helpers.flatten_tree(submission.comments)
			except:
				print("Found an error somewhere..") # too lazy to add worthwhile catches lol, just skip this for now
			for comment in flat_comments:
				try:
					author = comment.author
					if author.name != bot.name:
						has_keyword = any(string in comment.body for string in keywords)
						if comment.id not in already_done and has_keyword:
							chk = check_keyword(keywords, comment.body)
							print("Found keyword " + chk)
							comment.reply(replies[chk] + footer_txt)
							cursor.execute("""INSERT INTO parsed (id, comment_id) VALUES (NULL, ?);""", [comment.id])
							already_done.add(comment.id)
							connection.commit()
							cnt += 1
				except:
					print("Found an error somewhere..") # too lazy to add worthwhile catches lol, just skip this for now
		print("Parsing done. Trying again in 10 minutes. I commented " + str(cnt) + " times")
		cnt = 0
		time.sleep(1000)
	connection.close()

if __name__ == "__main__":
	main()
