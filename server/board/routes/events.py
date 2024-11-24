from fastapi import APIRouter, HTTPException, status, Body, Depends
from typing import List
from database.connection import get_session
from sqlmodel import select, Session
from models.events import Event, EventUpdate, Comment
from sqlalchemy.orm import joinedload



event_router = APIRouter()


events = []


# 이벤트 전체(목록) 조회 => GET /event/ => retrive_all_events() 전체 게시글용. 이용자 전체 열려있어야함
@event_router.get("/", response_model=List[Event])
def retrive_all_events(session=Depends(get_session)) -> List[Event]:
    statement = select(Event) # SQLModel의 select 함수를 이용해서 모든 데이터를 조회
    events = session.exec(statement)
    return events



# 이벤트 상세 조회1 => GET /event/{id} => retrive_event() 게시글 1개 용. 이용자 전체 열려있어야함
# @event_router.get("/{id}", response_model=Event)
# def retrive_event(id: int, session=Depends(get_session)) -> Event:
#     # for event in events:
#     #     if event.id == id:
#     #         return event

#     # 데이터베이스에서 해당 ID의 데이터를 조회
#     event = session.get(Event, id)  
#     if event:
#         return event
        
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail="일치하는 게시글이 존재하지 않습니다.",
#     )


# 이벤트 상세조회2
@event_router.get("/{id}", response_model=Event)
def retrive_event(id: int, session=Depends(get_session)) -> Event:
    # 이벤트와 관련된 댓글을 함께 로드
    # 에러가 발생하여 아래아래 코드로 교
    # event = session.exec(
    #     select(Event)
    #     .options(joinedload(Event.comments))  # Event와 연결된 Comment들을 함께 로드
    #     .where(Event.id == id)
    # ).first()
    #아래 코드로 교체됨
    event = session.query(Event).options(joinedload(Event.comments)).filter(Event.id == id).first()


    if event:
        return event
        
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="일치하는 게시글이 존재하지 않습니다.",
    )



# 게시글 등록
@event_router.post("/", status_code=status.HTTP_201_CREATED)
def create_event(data: Event = Body(...), session=Depends(get_session)) -> dict:
    # events.append(data)
    session.add(data)  	# 데이터베이스에 데이터를 추가
    session.commit()  	# 변경사항을 저장
    session.refresh(data)  	# 최신 데이터로 갱신
    return {"message": "이벤트가 정상적으로 등록되었습니다."}


# 이벤트 하나 삭제 => DELETE /event/{id} => delete_event() 게시글 삭제. 운영자 권한.
@event_router.delete("/{id}")
def delete_event(id: int, session=Depends(get_session)) -> dict:
    # for event in events:
    #     if event.id == id:
    #         events.remove(event)
    #         return {"message": "이벤트가 정상적으로 삭제되었습니다."}

    event = session.get(Event, id)
    if event:
        session.delete(event)
        session.commit()
        return {"message": "이벤트가 정상적으로 삭제되었습니다."}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="일치하는 이벤트가 존재하지 않습니다.",
    )


# 이벤트 전체 삭제 => DELETE /event/ => delete_all_events() 게시글 리셋. 운영자권한.
@event_router.delete("/")
def delete_all_events(session=Depends(get_session)) -> dict:
    # events.clear()

    statement = select(Event)
    events = session.exec(statement)

    for event in events:
        session.delete(event)

    session.commit()

    return {"message": "모든 이벤트가 정상적으로 삭제되었습니다."}



# 이벤트 수정 => PUT /event/{id} => update_event() 게시글 수정, 게시글 생성자 권한. 게시글id->유저id->해당 유저만 수정 가능하도록.
@event_router.put("/{id}", response_model=Event)
def update_event(id: int, data: EventUpdate, session=Depends(get_session)) -> Event:
    event = session.get(Event, id)
    if event:
        # 요청 본문으로 전달된 내용 중 값이 있는 항목들만 추출해서 dict 타입으로 변환
        event_data = data.dict(exclude_unset=True)
        # 테이블에서 조회한 결과를 요청을 통해서 전달된 값으로 변경
        for key, value in event_data.items():
            setattr(event, key, value)

        session.add(event)
        session.commit()
        session.refresh(event)

        return event
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="일치하는 이벤트가 존재하지 않습니다.",
    )

# # 코멘트 등록
# @event_router.post("/{id}/comments", status_code=201, tags=["Comment"])
# def add_comment(id: int, content: str = Body(...), user_id: int = Body(...), session: Session = Depends(get_session)):
#     event = session.get(Event, id)
#     if not event:
#         raise HTTPException(status_code=404, detail="이벤트가 존재하지 않습니다.")
    
#     # 코멘트 생성
#     comment = Comment(content=content, user_id=user_id, event_id=id)
    
#     session.add(comment)
#     session.commit()
#     session.refresh(comment)
    
#     return {"message": "코멘트가 정상적으로 등록되었습니다.", "comment": comment}

# 코멘트 삭제
@event_router.delete("/{event_id}/comments/{comment_id}", tags=["Comment"])
def delete_comment(event_id: int, comment_id: int, session: Session = Depends(get_session)):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="이벤트가 존재하지 않습니다.")
    
    comment = session.get(Comment, comment_id)
    if comment and comment.event_id == event_id:
        session.delete(comment)
        session.commit()
        return {"message": "코멘트가 정상적으로 삭제되었습니다."}
    
    raise HTTPException(status_code=404, detail="코멘트를 찾을 수 없거나 이벤트와 일치하지 않습니다.")




# 위에거랑 과연 뭐가 맞을까
@event_router.post("/{id}/comments", status_code=201, response_model=Comment, tags=["Comment"])
def add_comment(id: int, content: str = Body(...), user_id: int = Body(...), session: Session = Depends(get_session)):
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="이벤트가 존재하지 않습니다.")
    
    # 코멘트 생성
    comment = Comment(content=content, user_id=user_id, event_id=id)
    
    session.add(comment)
    session.commit()
    session.refresh(comment)
    
    return comment  # Comment 모델을 반환