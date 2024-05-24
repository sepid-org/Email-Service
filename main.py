from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import aiosmtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
load_dotenv()

app = FastAPI()

class EmailSchema(BaseModel):
    email: EmailStr
    subject: str
    body: str

async def send_email(email: EmailSchema):
    message = EmailMessage()
    message["From"] = "your_email@example.com"
    message["To"] = email.email
    message["Subject"] = email.subject
    message.set_content(email.body)

    try:
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
    await send_email(email)
    return {"message": "Email has been sent"}
