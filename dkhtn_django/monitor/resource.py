import datetime
import threading
import time

from dkhtn_django.monitor.models import Resource

interval = 10


class FuncItem:
    alpha, beta, gamma = 1, 1, 1

    def __init__(self, func_id, cpu, mem):
        self.cost = 0
        self.func_id = func_id
        self.cpu = cpu
        self.mem = mem
        self.running = True
        self.time = 0

    def update(self, cpu, mem):
        self.calculate((self.cpu + cpu) >> 1, (self.mem + mem) >> 1)
        self.cpu = cpu
        self.mem = mem
        self.time += interval
        self.running = True
        pass

    def calculate(self, cpu, mem):
        self.cost += FuncItem.alpha * cpu + FuncItem.beta * mem


def time_add(origin, new):
    origin_hour = origin.hour
    origin_minute = origin.minute
    origin_second = origin.second

    new_hour = new // 3600
    new_minute = (new - new_hour * 3600) // 60
    new_second = new - new_hour * 3600 - new_minute * 60

    second = (new_second + origin_second) % 60
    new_minute += (new_second + origin_second) // 60

    minute = (new_minute + origin_minute) % 60
    new_hour += (new_minute + origin_minute) // 60

    hour = origin_hour + new_hour
    return datetime.time(hour=hour, minute=minute, second=second)


class MonitorConsuming(threading.Thread):
    def __init__(self):
        super(MonitorConsuming, self).__init__()
        self.function_pool = {

        }

    def run(self) -> None:
        while True:
            # 调用API，返回函数ID、CPU占用、内存占用
            api = [{"func-id": "3", "cpu": 0.3, "mem": 1.2}]

            for item in self.function_pool.values():
                item.running = False

            for item in api:
                fid = item["func-id"]
                if fid in item.keys():
                    self.function_pool[fid].update(item["cpu"], item["mem"])
                else:
                    self.start_running(fid, item["cpu"], item["mem"])

            for item in list(self.function_pool.values()):
                if item.running is False:
                    item.update(0, 0)
                    self.end_running(item.func_id)
                    self.function_pool.pop(item.func_id)
            time.sleep(interval)

    def end_running(self, fid):
        func_item = self.function_pool[self]
        func = Resource.objects.filter(function_id=fid).first()
        call_time = func.call_times + 1
        running_time = time_add(func.running_time, func_item.time)

        cost = func.cost + func_item.cost
        Resource.objects.filter(function_id=self).update(call_times=call_time,
                                                         running_time=running_time,
                                                         cost=cost, state=1)

    def start_running(self, fid, cpu, mem):
        self.function_pool[self] = FuncItem(self, cpu, mem)
        Resource.objects.filter(function_id=fid).update(state=0)
