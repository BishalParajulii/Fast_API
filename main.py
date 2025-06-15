from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel

app = FastAPI()

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./interview.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class TopicDB(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    questions = relationship("QuestionDB", back_populates="topic", cascade="all, delete-orphan")

class QuestionDB(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    answer = Column(String)
    topic_id = Column(Integer, ForeignKey("topics.id"))
    topic = relationship("TopicDB", back_populates="questions")

Base.metadata.create_all(bind=engine)

# Pydantic Models
class QuestionCreate(BaseModel):
    text: str
    answer: str

class TopicCreate(BaseModel):
    name: str

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# API Endpoints
@app.post("/topics/")
async def create_topic(topic: TopicCreate, db: Session = Depends(get_db)):
    db_topic = TopicDB(name=topic.name)
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return {"id": db_topic.id, "name": db_topic.name}

@app.get("/topics/")
async def get_topics(db: Session = Depends(get_db)):
    return db.query(TopicDB).all()

@app.post("/topics/{topic_id}/questions/")
async def create_question(topic_id: int, question: QuestionCreate, db: Session = Depends(get_db)):
    db_topic = db.query(TopicDB).filter(TopicDB.id == topic_id).first()
    if not db_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    db_question = QuestionDB(text=question.text, answer=question.answer, topic_id=topic_id)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return {"id": db_question.id, "text": db_question.text, "answer": db_question.answer, "topic_id": topic_id}

@app.delete("/questions/{question_id}")
async def delete_question(question_id: int, db: Session = Depends(get_db)):
    db_question = db.query(QuestionDB).filter(QuestionDB.id == question_id).first()
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(db_question)
    db.commit()
    return {"message": "Question deleted successfully"}

@app.get("/add", response_class=HTMLResponse)
async def get_index(request: Request, db: Session = Depends(get_db)):
    topics = db.query(TopicDB).all()
    return templates.TemplateResponse("index.html", {"request": request, "topics": topics})

@app.get("/", response_class=HTMLResponse)
async def view_all(request: Request, db: Session = Depends(get_db)):
    topics = db.query(TopicDB).all()
    return templates.TemplateResponse("all_view.html", {"request": request, "topics": topics})

@app.delete("/delete-topic/{topic_id}")
async def delete_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(TopicDB).filter(TopicDB.id == topic_id).first()
    print(f"Attempting to delete topic with ID: {topic_id}, Found: {topic}") # Debug log
    if topic:
        db.delete(topic)
        db.commit()
        return {"message": "Topic deleted"}
    raise HTTPException(status_code=404, detail="Topic not found")