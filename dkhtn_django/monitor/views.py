# Create your views here.

import json

from django.http import HttpResponse

from Dkhtn_Django.dkhtn_django.monitor.models import *

states = ["running", "stop"]


def resource_query(request):
    # assert request.method == "GET"
    # 查询UID获取对应FuncId
    func_ids = ["2"]
    response = {"code": 400, "msg": "", "data": []}
    for func_id in func_ids:
        function = Resource.objects.filter(function_id=func_id).first()
        source = monitor(func_id)
        response["data"].append({
            "func-id": func_id,
            "state": states[function.state],
            "cpu": source[0],
            "memory": source[1],
            "run_time": function.running_time,
            "times": function.call_times,
            "error": function.error_times,
            "cost": function.cost
        })
    return HttpResponse(json.dumps(response))


def monitor(func_id):
    # 调用API，返回CPU、内存占用情况
    cpu, mem = 0, 0
    return cpu, mem


def add_item(func_id):
    Resource.objects.create(function_id=func_id, state=1, running_time=0, call_times=0, error_times=0, cost=0)


def delete_item(func_id):
    Resource.objects.filter(function_id=func_id).delete()
