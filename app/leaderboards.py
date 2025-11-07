from flask import render_template, Blueprint, redirect, url_for, request, abort, flash, make_response, current_app
from flask_user import login_required, current_user
from datatables import ColumnDT, DataTables
import time
from app.models import CharacterInfo, Leaderboard, db
from app import gm_level, log_audit
from app.luclient import translate_from_locale
import xmltodict
import xml.etree.ElementTree as ET
import json
from xml.dom import minidom

leaderboards_blueprint = Blueprint('leaderboards', __name__)

@leaderboards_blueprint.route('/', methods=['GET'])
@login_required
def index():

    #leaderboards_data = Leaderboard.query.all()

    #current_app.logger.warn(leaderboards_data.as_dict())
    #thisdict = []
    #for row in leaderboards_data:
    #    thisdict.append(row.as_dict())
        #current_app.logger.warn(row)
    #current_app.logger.warn(thisdict)
    #leaderboards_json = json.dumps(dict(leaderboards_data))
    leaderboards_json = {}

    return render_template(
        'leaderboards/index.html.j2',
        leaderboards_json=leaderboards_json
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
        ColumnDT(Leaderboard.timesPlayed),     # 2
        ColumnDT(Leaderboard.last_played),     # 3
        ColumnDT(CharacterInfo.name),          # 4
        ColumnDT(Leaderboard.game_id)          # 5
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
                {leaderboard["4"]}
            </a>
        """
    return data
