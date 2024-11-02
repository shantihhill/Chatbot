from app.constants import *
from app.chains import *
from app.flags import *
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse
from langserve import add_routes
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import os

#app definition
app = FastAPI(
    title="Chatbot Server",
    version="1.0",
    description="Chatbot API server for conversational qa",
)

#cors settings needed for web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")

#get endpoint for specific documents
@app.get("/downloadfile/{file_path:path}")
async def download_file(file_path: str):
    #add code to get document
    file_path = './' + file_path
    if os.path.exists(file_path): 
        return FileResponse(file_path)
    else:
        return HTTPException(status_code=404, detail="File not found")

#post endpoing for submitting chat flags
@app.post("/flags")
async def create_flag(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        chat = data.get('chat')
        chat = [message for exchange in chat for message in exchange]
        chat = "\n|\n".join(chat)
        comment = data.get('comment')
        flag = FlagData(chat=chat, comment=comment)
        db.add(flag)
        db.commit()
        db.refresh(flag)
        return {"id": flag.id, "chat": flag.chat, "comment": flag.comment, "date": flag.date}
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))

#get endpoint for retrieving submitted chat flags
@app.get("/flags", response_model=List[Dict[str, Any]])
def read_flags(db: Session = Depends(get_db)):
    try:
        flags = db.query(FlagData).all()
        return [
            {
                "id": flag.id,
                "chat": flag.chat,
                "comment": flag.comment,
                "date": flag.date
            }
            for flag in flags
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#adding route to conversational qa chain
add_routes(
    app,
    conversational_qa_chain,
    path="/model/conversational",
    enable_feedback_endpoint=True,
)

#adding route to simple qa chain
add_routes(
    app,
    simple_qa_chain,
    path="/model/simple",
    enable_feedback_endpoint=True,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)