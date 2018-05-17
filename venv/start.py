from flask import Flask
from flask import request
from pymongo import MongoClient
import datetime
app = Flask(__name__)


# preparing db objects
client = MongoClient()
db = client.wta_tools
tool_events = db.tool_events
tools = db.tools
users = db.users


@app.route('/')
def index():
	print('===============================\n')
	print("Root page visit!")
	print('\n===============================')
	return "root page"


# http://185.74.13.164:5000/wooga_photoshop_tools?tool_name=exporter&user_name=Anil&export_count=45
@app.route('/wooga_photoshop_tools', methods=['GET'])
def update_usage_in_db(*args):
	# check if the user exists, if not add to users
	user = users.find_one({"user_name": request.args['user_name']})
	if user is None:
		user_id = users.insert({"user_name": request.args['user_name']})
	else:
		user_id = user['_id']

	# check if tool exists, if not, add
	tool = tools.find_one({"tool_name": request.args['tool_name']})
	if tool is None:
		tool_id = tools.insert({"tool_name": request.args['tool_name']})
	else:
		tool_id = tool['_id']

	# create a tool event dict (for inserting into event collection),
	event_dict = {
		"timestamp": datetime.datetime.utcnow(),
		"user_id": user_id,
		"tool_id": tool_id,
	}

	# if tool is export tool, then also include the export count in event_data
	if request.args['tool_name'] == "exporter":
		event_dict['event_data'] = {"export_count": int(request.args['export_count'])}

	# insert event dict into events collection in db
	tool_events.insert_one(event_dict)
	return "here have a return"
