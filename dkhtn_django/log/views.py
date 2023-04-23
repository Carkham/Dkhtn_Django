from datetime import datetime

from django.http import JsonResponse

from .models import LogMessage


def request_error(response, msg):
    response["code"] = -1
    response["msg"] = msg
    return JsonResponse(response)


def query_log(request, func_id):
    response = {
        "code": 0,
        "msg": "",
        "data": {"logs": []}
    }
    try:
        assert request.method == "GET"
    except AssertionError:
        return request_error(response, "The type of your request is not GET")

    start_time = request.GET.get("startDatetime")
    end_time = request.GET.get("endDatetime")
    level = request.GET.get("level")
    keyword = request.GET.get("keyword")

    start_time = "2023-1-1T00:00" if start_time is None else start_time
    end_time = datetime.now().strftime("%Y-%m-%dT%H:%M") if end_time is None else end_time
    keyword = "" if keyword is None else keyword

    try:
        start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
        end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M")
    except ValueError:
        return request_error(response, "Your timestamp format is wrong")

    if level is None:
        logs = LogMessage.objects.filter(function_id=func_id,
                                         timestamp__range=(start_time, end_time),
                                         message__contains=keyword)
    else:
        logs = LogMessage.objects.filter(function_id=func_id,
                                         timestamp__range=(start_time, end_time),
                                         level=level,
                                         message__contains=keyword)

    for log in logs:
        response["data"]["logs"].append({
            "level": log.level,
            "timestamp": str(log.timestamp),
            "content": log.message
        })
    return JsonResponse(response)
