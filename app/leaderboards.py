from flask import render_template, Blueprint, redirect, url_for, request, abort, flash, make_response, current_app
from flask_user import login_required, current_user
from datatables import ColumnDT, DataTables
import time
from app.models import CharacterInfo, Leaderboard, db
from app.forms import LeaderboardsForm
from app import gm_level, log_audit
from app.luclient import translate_from_locale
import xmltodict
import xml.etree.ElementTree as ET
import json

leaderboards_blueprint = Blueprint('leaderboards', __name__)

# Load the activities from xml only once, because they do not change.
# Generated from: grep -o -iIP 'Activities_[0-9]+_ActivityName' locale.xml | grep -oE '[0-9]+' | sort -n | xargs printf '%s,' ; printf '\n'
activity_ids = [1,5,14,39,42,44,46,47,48,49,53,54,55,56,57,58,60,61,62,103,104,108,1864,1901,13951]
activities = []

# We need this in a function called with the app context so translate_from_locale can load app config to find the locale.xml
def populate_activities():
    if len(activities) > 0:
        return
    for a in activity_ids:
        name = translate_from_locale(f"Activities_{a}_ActivityName")
        activities.append((a, name))

@leaderboards_blueprint.route('/', methods=['GET','POST'])
@leaderboards_blueprint.route('/<id>/', methods=['GET','POST'])
@login_required
def index(id=1):
    form = LeaderboardsForm()
    if request.method == "POST":
        id = form.activity.data
        current_app.logger.warn(f"Got a POST for id={id}")

    populate_activities()
    for pair in activities:
        form.activity.choices.append(pair)

    leaderboards_data = Leaderboard.query.filter(Leaderboard.game_id == id).all()

    current_app.logger.warn(leaderboards_data)

    current_app.logger.warn(f"Right before render for {request.method}, using id={id}")
    return render_template(
        'leaderboards/index.html.j2',
        form = form,
        id = id
    )

@leaderboards_blueprint.route('/get/<id>', methods=['GET'])
@login_required
def get(id):
    # https://explorer.lu/activities
    # foot races counting seconds elapsed: 1 46 47 49 53
    # foot races counting time left: 48
    # race tracks: 39 42 54 60
    #leaderboards_data = Leaderboard.query.filter(
    #    Leaderboard.game_id == id_
    #).all()
    # Category determines what columns are displayed
    columns = [
        ColumnDT(Leaderboard.character_id),    # 0
        ColumnDT(Leaderboard.primaryScore),    # 1
        ColumnDT(Leaderboard.secondaryScore),  # 2
        ColumnDT(Leaderboard.tertiaryScore),   # 3
        ColumnDT(Leaderboard.timesPlayed),     # 4
        ColumnDT(Leaderboard.last_played),     # 5
        ColumnDT(CharacterInfo.name),          # 6
        ColumnDT(Leaderboard.game_id)          # 7
    ]
    query = db.session.query().select_from(Leaderboard).join(CharacterInfo).filter((Leaderboard.game_id == id) & (CharacterInfo.id == Leaderboard.character_id))
    #current_app.logger.warn(query)
    params = request.args.to_dict()
    rowTable = DataTables(params, query, columns)
    data = rowTable.output_result()
    for leaderboard in data["data"]:
        id = leaderboard["0"]
        leaderboard["0"] = f"""
            <div class="d-none">{id}</div>
            <a role="button" class="btn btn-primary btn btn-block"
                href='{url_for('characters.view', id=id)}'>
                {leaderboard["6"]}
            </a>
        """
    return data
