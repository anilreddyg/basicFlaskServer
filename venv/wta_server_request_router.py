from bson import ObjectId
from flask import Flask
from flask import request
from flask import  render_template
from pymongo import MongoClient
import datetime
from distutils.version import LooseVersion
app = Flask(__name__)


# preparing db objects
client = MongoClient()
db = client.wta_tools
# collections
tool_events = db.tool_events
db_tools = db.tools
db_users = db.users
db_packages = db.packages


@app.route('/reports')
def render_reports():
	print("\nreceived report request at {}\n".format(datetime.datetime.now()))
	# EXPORT TABLE
	export_report = list()
	for user in db_users.find():
		export_report.append({'user_name': user['user_name']})
	# print(export_table)

	# for each user, get the export count
	exporter_tool_id = db_tools.find_one({"tool_name": "exporter"})['_id']
	total_exported_items = 0
	for i, export_report_row in enumerate(export_report):
		export_calls = 0
		exported_items = 0
		user_id = db_users.find_one({"user_name":export_report_row['user_name']})['_id']
		# find all export events related to the current user
		for export_event in tool_events.find({"tool_id": ObjectId(exporter_tool_id), "user_id": ObjectId(user_id)}):
			export_calls += 1
			exported_items += export_event['event_data']['export_count']
		total_exported_items += exported_items
		export_report[i].update({"export_calls":export_calls, "exported_items":exported_items})
		# print("{} , {} , {}".format(export_table[i]['user_name'], export_table[i]['export_calls'], export_table[i]['exported_items']))

	# TOOLS REPORT
	tools_report = list()
	for tool in db_tools.find():
		tools_report.append({ 'tool_name': tool['tool_name']})
	# print(tools_report)

	# for each tool in the tool report, check the tool events for usage
	for i, tools_report_row in enumerate(tools_report):
		tool_id = db_tools.find_one({"tool_name": tools_report_row['tool_name']})['_id']
		tool_usage_count = 0
		for tool_event in tool_events.find({"tool_id": ObjectId(tool_id)}):
			tool_usage_count += 1
		tools_report[i].update({"tool_usage_count":tool_usage_count})
		# print("{} {}".format(tools_report[i]['tool_name'], tools_report[i]['tool_usage_count']))
	return render_template('reports.html', export_table=export_report, tools_table=tools_report, total_exported_items=total_exported_items)


# http://localhost:5000/wooga_photoshop_tools?tool_name=exporter&user_name=Anil&export_count=45
@app.route('/wooga_photoshop_tools', methods=['GET'])
def update_usage_in_db(*args):
	print("\nRegistered tool usage!\n")
	# check if the user exists, if not add to users
	user = db_users.find_one({"user_name": request.args['user_name']})
	if user is None:
		user_id = db_users.insert({"user_name": request.args['user_name']})
	else:
		user_id = user['_id']

	# check if tool exists, if not, add
	tool = db_tools.find_one({"tool_name": request.args['tool_name']})
	if tool is None:
		tool_id = db_tools.insert({"tool_name": request.args['tool_name']})
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


# http://localhost:5000/check_package_version?package_id=com.wta-photoshop&current_version=0.0.1
@app.route('/check_package_version', methods=['GET'])
def check_package_version(*args):
	print("\nreceived version request at {}\n".format(datetime.datetime.now()))
	latest_version = db_packages.find_one({"package_id":request.args['package_id']})['latest_version']
	current_version = request.args['current_version']
	if LooseVersion(latest_version) > LooseVersion(current_version):
		return "outdated"
	return "up to date"