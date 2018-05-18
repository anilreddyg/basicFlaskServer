from bson import ObjectId
from flask import Flask
from flask import request
from flask import  render_template
from pymongo import MongoClient
import datetime
app = Flask(__name__)


# preparing db objects
client = MongoClient()
db = client.wta_tools
tool_events = db.tool_events
tools = db.tools
users = db.users


@app.route('/reports')
def render_reports():
	# store user dicts in a list
	export_table = list()
	for user in users.find():
		export_table.append({'user_name': user['user_name']})
	# print(export_table)

	# for each user, get the export count
	exporter_tool_id = tools.find_one({"tool_name": "exporter"})['_id']
	for i, export_table_row in enumerate(export_table):
		export_calls = 0
		exported_items = 0
		user_id = users.find_one({"user_name":export_table_row['user_name']})['_id']
		# find all export events related to the current user
		for export_event in tool_events.find({"tool_id": ObjectId(exporter_tool_id), "user_id": ObjectId(user_id)}):
			export_calls += 1
			exported_items += export_event['event_data']['export_count']
		export_table[i].update({"export_calls":export_calls, "exported_items":exported_items})
		print("{} , {} , {}".format(export_table[i]['user_name'], export_table[i]['export_calls'], export_table[i]['exported_items']))
	# display users, their exports and total exported items
	# return "here have a return"
	return render_template('reports.html', export_table=export_table)


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
