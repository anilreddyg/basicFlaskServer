from flask import Flask
from flask import request
from pymongo import MongoClient
app = Flask(__name__)


client = MongoClient()
db = client.ToolUsage
psData = db.PhotoshopData


@app.route('/')
def index():
	print('===============================\n')
	print("Root page visit!")
	# print(psData.find_one({"user":"Trilok"})['exports'])
	print('\n===============================')
	return "Connected to this Database: '{}'<br> and referencing the collection '{}'" .format(db.name,psData.name)


@app.route('/export',  methods=['GET'])
def update_export_usage_in_db():
	print('===============================')
	print("\n'{0}' exported '{1}' items using the export panel\n".format(request.args['user'], request.args['exportCount']))
	user = request.args['user']
	export_count = int(request.args['exportCount'])
	update_usage_in_db(user, 'exports', export_count)
	print('\n===============================')
	return 'export tool used!'


@app.route('/toolBox', methods=['GET'])
def update_toolbox_usage_in_db():
	print('===============================')
	print("\n'{0}' used the '{1}' tool from the toolbox\n" .format(request.args['user'], request.args['toolName']))
	user = request.args['user']
	tool_name = request.args['toolName'].lower()
	update_usage_in_db(user, tool_name)
	print('\n===============================')
	return 'tool boxing!'


def update_usage_in_db(*args):
	inc_val = 1
	if len(args) == 3:
		inc_val = args[2]
	user_data = psData.find_one({"user": args[0]})
	# if user does not exist insert document with tool usage of 1
	if user_data is None:
		psData.insert_one({"user": args[0], args[1]: inc_val})
		print("Created new user: {}".format(args[0]))
	else:
		psData.update({"_id": user_data['_id']}, {"$inc": {args[1]: inc_val}})
		print("Updated {}'s '{}' usage count by {}".format(args[0], args[1], inc_val))
