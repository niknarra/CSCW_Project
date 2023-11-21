import matplotlib.pyplot as plt
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import mimetypes
from email.message import EmailMessage
from email import encoders
from email.mime.base import MIMEBase
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import HumanMessage
import os
import smtplib, ssl
from email.message import EmailMessage


audio_transcript_file = "C:/Users/chpre/OneDrive/Documents/Zoom/meeting_trasncripts.txt"

def email_triggering(email_body, to_email):
    # email details
    sender_email = "sevideoconf@gmail.com" 
    receiver_email = to_email
    subject = "Personlized Meeting minutes and remainders"
    body = email_body
    #image_file = "client_graph.png"

    # create a multipart message object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # add body to the message
    msg.attach(MIMEText(body, 'plain'))
    
    attachment = open(audio_transcript_file, "rb")
      
    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')
      
    # To change the payload into encoded form
    p.set_payload((attachment).read())
      
    # encode into base64
    encoders.encode_base64(p)
       
    p.add_header('Content-Disposition', "attachment; filename= %s" % "audio_transcript_file.txt")
      
    # attach the instance 'p' to instance 'msg'
    msg.attach(p)


    # connect to SMTP server and send email
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    password = "uigp uyyo igri twvy"

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.send_message(msg, from_addr=sender_email, to_addrs=receiver_email)


detected_text = "Following is a meeting audio trasncripts generated during a remote zoom meeting : \n"

file1 = open(audio_transcript_file,"r+")
data = file1.read()

detected_text = detected_text + str(data)

detected_text = detected_text + "\n \n " + "assume you are an meeting minutes writing expert. your task is to generate meeting minutes and also geneerate task alerts/deadlines w.r.t. participants, task allocations, and remainders. Construct your answers by referring to the provided context and your general knowledge. " + "\n"
#print(detected_text)

os.environ["OPENAI_API_KEY"] = "" # place your openai key here

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.create_documents([detected_text])

directory = "index_store_soccomp"
vector_index = FAISS.from_documents(texts, OpenAIEmbeddings())
vector_index.save_local(directory)
vector_index = FAISS.load_local("index_store_soccomp", OpenAIEmbeddings())
retriever = vector_index.as_retriever(search_type="similarity", search_kwargs={"k": 6})
conv_interface = ConversationalRetrievalChain.from_llm(ChatOpenAI(model_name="gpt-3.5-turbo", streaming=True, callbacks=[StreamingStdOutCallbackHandler()], temperature=0), retriever=retriever)


chat_history = []

query = "assume you are an meeting minutes writing expert. the location of the meeting is remote, and the attendees are Nikhil, premith, and stanley, meeting time is 10/17/2023 at 12:54PM. your task is to generate meeting minutes and also generate task alerts/deadlines w.r.t. participants, task allocations, and remainders"

result = conv_interface({"question": query, "chat_history": chat_history})
print(result["answer"])


email_triggering(str(result["answer"]), "cpremithkumar@vt.edu")
email_triggering(str(result["answer"]), "nikhilnarra@vt.edu")
email_triggering(str(result["answer"]), "stanleygabriel97@vt.edu")