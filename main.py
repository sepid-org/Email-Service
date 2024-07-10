from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from jinja2 import Environment, FileSystemLoader
import aiosmtplib
from email.message import EmailMessage
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
import httpx

load_dotenv()

app = FastAPI()

class EmailSchema(BaseModel):
    email: list[str]# type: ignore
    subject: str
    body: dict



async def send_email(email: EmailSchema):
    env = Environment(loader=FileSystemLoader('.'))
    if email.body['type'] == 1:
        template = env.get_template('templates/greeting.html')
        template.render(name=email.body['name'])
    if email.body['type'] == 2:
        template = env.get_template('templates/news.html')
        template.render(news=email.body['news'])
    if email.body['type'] == 3:
        template = env.get_template('templates/verify.html')
        template.render(code=email.body['code'])


    message = EmailMessage()
    message["From"] = "your_email@example.com"
    # message["To"] = email.email
    message["Subject"] = email.subject
    # message.set_content(email.body)
    message.add_alternative(template, subtype='html')

    try:
        for i in email.email:
            message["To"] = i
            await aiosmtplib.send(
                message,
                hostname="smtp.gmail.com",
                port=587,
                start_tls=True,
                username="sepid.platform@gmail.com",
                password=os.getenv('GMAIL_KEY' ,"xxxxxxxx")
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-email/")
async def send_email_endpoint(email: EmailSchema):
    print('hi')
    await send_email(email)
    return {"message": "Email has been sent"}

class DataSchema(BaseModel):
    key: str
    value: str

TARGET_URL = "http://127.0.0.1:8000/send-email/"

@app.post("/proxy/")
async def proxy_post(data: EmailSchema):
    print(data)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(TARGET_URL, json=data.dict())
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Request to {TARGET_URL} failed with status {e.response.status_code}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Request successful", "data": response.json()}
