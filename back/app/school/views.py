from flask import jsonify, request, current_app
from datetime import datetime
from sqlalchemy import func

from app.school import api
from app.utils.response_code import RET
from app.models import School


@api.route('/detail', methods=['GET', 'POST'])
def get_school_detail():
    ID = request.args.get('id')
    data = []
    if (ID):
        try:
            school = School.query.filter(School.ID == ID).scalar()
        except Exception as e:
            current_app.logger.debug(e)
            return jsonify(code=RET.DBERR, msg='查询院校失败')
        if (school):
            data.append(
                {
                    'ID': school.ID,
                    'Name': school.name,
                    'type': school.type,
                    'StudentNum': school.studentNum,
                    'introduce': school.introduce,
                    'Date': school.date
                }
            )
        else:
            return jsonify(code=RET.NODATA, msg='院校不存在')
    else:
        try:
            schools = School.query.all()
        except Exception as e:
            current_app.logger.debug(e)
            return jsonify(code=RET.DBERR, msg='查询院校失败')
        for school in schools:
            data.append(
                {
                    'ID': school.ID,
                    'Name': school.name,
                    'type': school.type,
                    'StudentNum': school.studentNum,
                    'Introduce': school.introduce,
                    'Date': school.date
                }
            )
    return jsonify(code=RET.OK, data=data, msg='查找成功')


@api.route('/info', methods=['GET', 'POST'])
def get_school_info():
    try:
        universityNum = School.query.filter(School.type == 0).count()
        academyNum = School.query.filter(School.type == 1).count()
        schoolNum = School.query.filter(School.type == 2).count()
        date = datetime.utcnow()
    except Exception as e:
        current_app.logger.debug(e)
        return jsonify(code=RET.DBERR, msg='查询信息失败')
    data = {
        'UniversityNum': universityNum,
        'AcademyNum': academyNum,
        'SchoolNum': schoolNum,
        'Date': date
    }
    return jsonify(code=RET.OK, data=data, msg='查询成功')
