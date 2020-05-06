from flask import jsonify, request, current_app
from sqlalchemy.sql import func
from app import db

from app.community import api
from app.models import Community
from app.utils.response_code import RET

from datetime import datetime


@api.route('/detail', methods=['GET', 'POST'])
def get_detail():
    ID = request.args.get('id')
    data = []
    if (ID):
        try:
            community = Community.query.filter(Community.ID == ID).scalar()
        except Exception as e:
            current_app.logger.debug(e)
            return jsonify(code=RET.DBERR, msg='查询社区失败')
        if(community):
            data.append(
                {
                    'ID':community.ID,
                    'Name':community.name,
                    'FamilyNum':community.familyNum,
                    'ServerNum':community.serverNum,
                    'Date':community.date
                }
            )
        else:
            return jsonify(code=RET.NODATA, msg='社区不存在')
    else:
        try:
            communitys = Community.query.all()
        except Exception as e:
            current_app.logger.debug(e)
            return jsonify(code=RET.DBERR, msg='查询社区失败')
        for community in communitys:
            data.append(
                {
                    'ID': community.ID,
                    'Name': community.name,
                    'FamilyNum': community.familyNum,
                    'ServerNum': community.serverNum,
                    'Date': community.date
                }
            )
    return jsonify(code=RET.OK, data=data, msg='查找成功')

@api.route('/info', methods=['GET', 'POST'])
def get_community_info():
    try:
        communityNum = Community.query.count()
        familyNum = Community.query.with_entities(func.sum(Community.familyNum)).scalar()
        serverNum = Community.query.with_entities(func.sum(Community.serverNum)).scalar()
        date = datetime.utcnow()
    except Exception as e:
        current_app.logger.debug(e)
        return jsonify(code=RET.DBERR, msg='查询信息失败')
    data = {
        'CommunityNum':communityNum,
        'FamilyTotalNum':int(familyNum),
        'ServerTotalNum':int(serverNum),
        'Date':date
    }
    return jsonify(code=RET.OK, data=data, msg='查询成功')

