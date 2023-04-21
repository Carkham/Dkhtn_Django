import json
from datetime import datetime

from django.http import JsonResponse

from .models import LogMessage


def query_log(request, func_id):
    response = {
        "code": 0,
        "msg": "",
        "data": {"logs": []}
    }

    try:
        assert request.method == "GET"
        start_time = request.GET.get("startDatetime")
        end_time = request.GET.get("endDatetime")
        start_time = datetime.strptime(start_time, "%y-%m-%d %H:%M")
        end_time = datetime.strptime(end_time, "%y-%m-%d %H:%M")
        level = request.GET.get("level")
        keyword = request.GET.get("keyword")
    except:
        response["code"] = -1
        response["msg"] = "Error occurs in your http request"
        return JsonResponse(json.dumps(response))

    try:
        logs = LogMessage.objects.filter(function_id=func_id,
                                         timestamp__range=(start_time, end_time),
                                         level=level,
                                         message__contains=keyword)
    except:
        response["code"] = -1
        response["msg"] = "Error occurs while querying log database"
        return JsonResponse(json.dumps(response))

    for log in logs:
        response["data"]["logs"].append({
            "level": log.level,
            "timestamp": log.timestamp,
            "content": log.message
        })
    return JsonResponse(json.dumps(response))
