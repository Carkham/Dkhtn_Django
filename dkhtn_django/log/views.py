import json
from datetime import datetime

from django.http import JsonResponse

from .models import LogMessage


def request_error(response, msg):
    response["code"] = -1
    response["msg"] = msg
    return JsonResponse(json.dumps(response))


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
        start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
        end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M")
        level = request.GET.get("level")
        keyword = request.GET.get("keyword")
    except AssertionError:
        return request_error(response, "The type of your request is not GET")
    except ValueError:
        return request_error(response, "Your timestamp format is not appropriate")
    except KeyError:
        return request_error(response, "The request does not contain certain keys")

    try:
        logs = LogMessage.objects.filter(function_id=func_id,
                                         timestamp__range=(start_time, end_time),
                                         level=level,
                                         message__contains=keyword)
    except ValueError:
        return request_error(response, "ValueError occurs while querying log database")
    except KeyError:
        return request_error(response, "KeyError occurs while querying log database")

    for log in logs:
        response["data"]["logs"].append({
            "level": log.level,
            "timestamp": str(log.timestamp),
            "content": log.message
        })
    return JsonResponse(json.dumps(response))
