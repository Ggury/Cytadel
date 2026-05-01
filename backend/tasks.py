from  worker import celery_app
import time

@celery_app.task(name = "send_activation_code")
def send_activation_code(email:str, key:str):
    print(f"Sending code to {email}")
    print(f"Activation key: {key}")
    return True
