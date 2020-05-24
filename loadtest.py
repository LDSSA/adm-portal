import os

from locust import HttpUser, TaskSet, task, between


# locust -f loadtest.py

EMAIL = os.environ["ADM_LOAD_TEST_EMAIL"]
PASSWORD = os.environ["ADM_LOAD_TEST_PASSWORD"]


class LoadTestTasks(TaskSet):
    @task(1)
    def sleep_long(self):
        payload = {
            "email": EMAIL,
            "password": PASSWORD,
            "duration": 11,
        }
        self.client.post("/loadtest/sleep/12", json=payload)

    @task(3)
    def sleep_short(self):
        payload = {
            "email": EMAIL,
            "password": PASSWORD,
        }
        self.client.post("/loadtest/sleep/1", json=payload)


class LoadTestUser(HttpUser):
    host = "http://0.0.0.0:8000"
    wait_time = between(5, 15)
    tasks = [LoadTestTasks]
