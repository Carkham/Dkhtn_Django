# Create your views here.

from django.http import JsonResponse

from .models import Functions


def resource_query(request):
    response = {"code": 0, "msg": "", "data": []}
    assert request.method == "GET"
    session_id = request.COOKIES.get("session_id")
    user_id = "114514"
    resources = Functions.objects.filter(user_id=user_id)
    for resource in resources:
        cpu, mem = monitor(resource.function_id)
        response["data"].append({
            "func-id": resource.function_id,
            "state": 1,
            "cpu": cpu,
            "memory": mem,
            "run_time": 0,
            "times": resource.call_count,
            "error": resource.error_count,
            "cost": 0
        })
    return JsonResponse(response)


def monitor(func_id):
    # 调用API，返回CPU、内存占用情况
    cpu, mem = 0, 0
    return cpu, mem
