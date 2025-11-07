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

@leaderboards_blueprint.route('/', methods=['GET','POST'])
@leaderboards_blueprint.route('/<id>/', methods=['GET','POST'])
@login_required
def index(id=1):
    form = LeaderboardsForm()
    if request.method == "POST":
        id = form.activity.data
        current_app.logger.warn(f"Got a POST for id={id}")

    # WIP: populate the choices here
    choices = [
        {"id":1, "name": "Avant Gardens Monument Race"},
        {"id":5, "name": "Avant Gardens Survival"},
    ]
    #for c in choices:
    #    form.activity.choices.append((c["id"],c["name"]))

    # Initial form loads something
    leaderboards_data = Leaderboard.query.filter(Leaderboard.game_id == id).all()

    current_app.logger.warn(leaderboards_data)
    #thisdict = []
    #for row in leaderboards_data:
    #    thisdict.append(row.as_dict())
    #    current_app.logger.warn(row)
    #current_app.logger.warn(thisdict)
    #leaderboards_json = json.dumps(dict(leaderboards_data))
    leaderboards_json = {}

    current_app.logger.warn(f"Right before render for {request.method}, using id={id}")
    return render_template(
        'leaderboards/index.html.j2',
        leaderboards_json = leaderboards_json,
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
