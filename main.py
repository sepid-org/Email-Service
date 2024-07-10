from typing import List, Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import aiosmtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()


class EmailSchema(BaseModel):
    email: List[str]
    subject: str
    body: dict
    template: Literal['greeting', 'news', 'verification']


def read_html_template(file_path: str) -> str:
    with open(file_path, 'r') as file:
        template = file.read()
    return template


async def send_email(email: EmailSchema):
    if email.template == 'greeting':
        template = read_html_template('templates/greeting.html')
        html_content = template.replace('{{ name }}', email.body['name'])
    elif email.template == 'news':
        template = read_html_template('templates/news.html')
        html_content = template.replace('{{ news }}', email.body['news'])
    elif email.template == 'verification':
        template = read_html_template('templates/verification.html')
        html_content = template.replace('{{ code }}', email.body['code'])
    else:
        raise HTTPException(status_code=400, detail="Invalid email body type")

    message = EmailMessage()
    message["From"] = "sepid.platform@gmail.com"
    message["Subject"] = email.subject
    message.add_alternative(html_content, subtype='html')

    try:
        for recipient in email.email:
            message["To"] = recipient
            await aiosmtplib.send(
                message,
                hostname="smtp.gmail.com",
                port=465,
                use_tls=True,
                username="sepid.platform@gmail.com",
                password=os.getenv('GMAIL_KEY', "xxxxxxxx")
            )
    except aiosmtplib.SMTPException as smtp_error:
        raise HTTPException(
            status_code=500, detail=f"SMTP error: {smtp_error}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"General error: {e}")


@app.post("/send-email/")
async def send_email_endpoint(email: EmailSchema):
    await send_email(email)
    return {"message": "Email has been sent"}
