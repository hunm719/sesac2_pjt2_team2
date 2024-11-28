from fastapi import APIRouter, HTTPException, status, Body, Depends, UploadFile, File
from typing import List
from board.database.connection import get_session
from sqlmodel import select, Session
from board.models.events import Board, BoardUpdate, Comment
from sqlalchemy.orm import joinedload
from fastapi.encoders import jsonable_encoder
#, UploadFile, File 추가, 아래 추가
import shutil
from pathlib import Path
from fastapi.responses import FileResponse

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import uuid, os

from board.models.users import UserSignIn, UserSignUp
from board.models.events import User

user_router = APIRouter()

board_router = APIRouter()

# 이미지 저장 디렉토리 설정(추가)
UPLOAD_DIR = Path("uploads/")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 게시판 전체 조회 => GET /board/ => retrieve_all_boards()
@board_router.get("/", response_model=List[Board])
def retrieve_all_boards(session=Depends(get_session)) -> List[Board]:
    statement = select(Board)
    boards = session.exec(statement)
    return boards


# 게시판 상세 조회 => GET /board/{id} => retrieve_board()
@board_router.get("/{id}", response_model=Board)
def retrieve_board(id: int, session=Depends(get_session)) -> Board:
    board = session.query(Board).options(joinedload(Board.comments)).filter(Board.id == id).first()

    if board:
        return board
        
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="일치하는 게시글이 존재하지 않습니다.",
    )


# # 게시글 등록 => POST /board/ => create_board()
# @board_router.post("/", status_code=status.HTTP_201_CREATED)
# def create_board(data: Board = Body(...), session=Depends(get_session)) -> dict:
#     session.add(data)  # 데이터베이스에 데이터를 추가
#     session.commit()  # 변경사항을 저장
#     session.refresh(data)  # 최신 데이터로 갱신
#     return {"message": "게시글이 정상적으로 등록되었습니다.", "data": data}

#새로 추가한 포스트(프론트용)
@board_router.post("/", status_code=status.HTTP_201_CREATED)
def create_board(data: BoardUpdate = Body(...), session: Session = Depends(get_session)) -> dict:
    # 새로운 게시글 생성
    new_board = Board(**data.dict())  # Board 모델의 필드에 맞게 데이터를 할당

    # 게시글을 데이터베이스에 추가
    session.add(new_board)
    session.commit()  # 변경사항 저장
    session.refresh(new_board)  # 최신 데이터로 갱신
    
    return {"message": "게시글이 정상적으로 등록되었습니다.", "data": new_board}

# 게시글 작성 및 이미지 업로드 => POST /board/upload/
@board_router.post("/upload/", status_code=status.HTTP_201_CREATED)
def create_board_with_image(
    title: str = Body(...),
    description: str = Body(...),
    tags: List[str] = Body(default=[]),
    user_id: str = Body(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    #    # 유저 ID가 존재하는지 데이터베이스에서 확인
    # user = session.exec(select(User).where(User.id == user_id)).first()
    
    # if not user:
    #     raise HTTPException(status_code=404, detail="유저 ID를 찾을 수 없습니다.")

    # 유저 ID가 존재하는지 UserSignUp 테이블에서 확인
    user = session.exec(select(User).where(User.user_id == user_id)).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="유저 ID를 찾을 수 없습니다.")


    # 파일 확장자 추출
    extension = Path(file.filename).suffix.lower()
    if extension not in [".jpg", ".jpeg", ".png", ".gif"]:
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")

    # 새 파일 이름 생성
    new_filename = f"{uuid.uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / new_filename

    # 파일 저장
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 게시글 생성
    new_board = Board(
        title=title,
        description=description,
        imgUrl=str(file_path),  # 파일 경로 저장
        tag=tags,
        user_id=user_id,
    )
    session.add(new_board)
    session.commit()
    session.refresh(new_board)

    return {
        "message": "게시글이 정상적으로 등록되었습니다.",
        "data": new_board,
        "image_url": str(file_path),
    }

# 게시글 삭제 => DELETE /board/{id} => delete_board()
@board_router.delete("/{id}")
def delete_board(id: int, session=Depends(get_session)) -> dict:
    board = session.get(Board, id)
    if board:
        session.delete(board)
        session.commit()
        return {"message": "게시글이 정상적으로 삭제되었습니다."}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="일치하는 게시글이 존재하지 않습니다.",
    )


# 게시글 전체 삭제 => DELETE /board/ => delete_all_boards()
@board_router.delete("/")
def delete_all_boards(session=Depends(get_session)) -> dict:
    statement = select(Board)
    boards = session.exec(statement)

    for board in boards:
        session.delete(board)

    session.commit()

    return {"message": "모든 게시글이 정상적으로 삭제되었습니다."}


# 게시글 수정 => PUT /board/{id} => update_board()
@board_router.put("/{id}", response_model=Board)
def update_board(id: int, data: BoardUpdate, session=Depends(get_session)) -> Board:
    board = session.get(Board, id)
    if board:
        board_data = data.dict(exclude_unset=True)
        for key, value in board_data.items():
            setattr(board, key, value)
        # 게시글 수정 시 updated_at을 현재 시간으로 설정
        board.updated_at = datetime.now(ZoneInfo("Asia/Seoul"))

        session.add(board)
        session.commit()
        session.refresh(board)

        return board
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="일치하는 게시글이 존재하지 않습니다.",
    )


# 코멘트 등록 => POST /board/{id}/comments => add_comment()
@board_router.post("/{id}/comments", status_code=201, response_model=Comment, tags=["Comment"])
def add_comment(id: int, content: str = Body(...), user_id: int = Body(...), session: Session = Depends(get_session)):
    board = session.get(Board, id)
    if not board:
        raise HTTPException(status_code=404, detail="게시글이 존재하지 않습니다.")
    
    comment = Comment(content=content, user_id=user_id, board_id=id)
    session.add(comment)
    session.commit()
    session.refresh(comment)
    
    return comment


# 코멘트 삭제 => DELETE /board/{id}/comments/{comment_id} => delete_comment()
@board_router.delete("/{board_id}/comments/{comment_id}", tags=["Comment"])
def delete_comment(board_id: int, comment_id: int, session: Session = Depends(get_session)):
    board = session.get(Board, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="게시글이 존재하지 않습니다.")
    
    comment = session.get(Comment, comment_id)
    if comment and comment.board_id == board_id:
        session.delete(comment)
        session.commit()
        return {"message": "코멘트가 정상적으로 삭제되었습니다."}
    
    raise HTTPException(status_code=404, detail="코멘트를 찾을 수 없거나 게시글과 일치하지 않습니다.")

#전체 코멘트 조회
@board_router.get("/{id}/comments", response_model=List[Comment], tags=["Comment"])
def get_event_comments(id: int, session=Depends(get_session)) -> List[Comment]:
    # 특정 이벤트에 연결된 댓글 가져오기
    event = (
        session.query(Board)
        .options(joinedload(Board.comments))  # Event와 관련된 Comment를 미리 로드
        .filter(Board.id == id)
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {id}에 해당하는 이벤트가 없습니다.",
        )
    
    # 댓글 반환
    comments = event.comments  # 관계로 불러온 Comment 리스트
    if not comments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {id} 이벤트에 댓글이 없습니다.",
        )
    
    return jsonable_encoder(comments)


# 이미지 업로드 => POST /board/{id}/image => upload_image()
@board_router.post("/{id}/image", status_code=status.HTTP_201_CREATED, tags=["Image"])
async def upload_image(id: int, file: UploadFile = File(...), session: Session = Depends(get_session)):
    # 게시글이 존재하는지 확인
    board = session.get(Board, id)
    if not board:
        raise HTTPException(status_code=404, detail="게시글이 존재하지 않습니다.")
    
    # 새 파일 이름 생성: 게시글 ID + 원본 파일 확장자
    extension = Path(file.filename).suffix  # 파일 확장자 추출
    new_filename = f"{id}_{uuid.uuid4().hex}{extension}"  # ID와 UUID를 결합한 새로운 파일 이름

    # 파일 저장
    file_path = UPLOAD_DIR / new_filename  # 새 파일 이름으로 저장
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # 파일 URL 반환
    file_url = f"/board/{id}/image/{new_filename}"  # 새 파일 이름을 URL에 반영
    
    # 파일 URL을 게시글에 추가할 수도 있습니다
    board.imgUrl = file_url
    session.add(board)
    session.commit()
    
    return {"filename": file.filename, "url": file_url}

# 이미지 조회 => GET /board/{id}/image/{image_name} => get_image()
@board_router.get("/{id}/image", tags=["Image"])
def get_image(id: int, session: Session = Depends(get_session)):
    # 게시글이 존재하는지 확인
    board = session.get(Board, id)
    if not board or not board.imgUrl:
        raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다.")
    
    # 이미지 파일 이름 추출 (imgUrl에 저장된 경로에서 파일명만 추출)
    image_name = Path(board.imgUrl).name  # /board/{id}/image/{image_name}에서 {image_name}만 추출
    
    # 파일 경로
    image_path = UPLOAD_DIR / image_name
    
    # 파일이 존재하는지 확인
    if image_path.exists():
        return FileResponse(image_path)
    
    raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다.")

#이미지 삭제
@board_router.delete("/{id}/image", status_code=status.HTTP_204_NO_CONTENT, tags=["Image"])
def delete_image(id: int, session: Session = Depends(get_session)):
    # 게시글이 존재하는지 확인
    board = session.get(Board, id)
    
    # id가 0인 경우에도 게시글을 찾을 수 있도록 명확히 처리
    if not board:
        raise HTTPException(status_code=404, detail=f"ID가 {id}인 게시글이 존재하지 않습니다.")
    
    # 게시글에 이미지가 연결되어 있는지 확인
    if not board.imgUrl:
        raise HTTPException(status_code=404, detail="이미지가 존재하지 않습니다.")
    
    # 이미지 파일 이름 추출 (imgUrl에 저장된 경로에서 파일명만 추출)
    image_name = Path(board.imgUrl).name  # /board/{id}/image/{image_name}에서 {image_name}만 추출
    
    # 파일 경로
    image_path = UPLOAD_DIR / image_name
    
    # 파일이 존재하는지 확인 후 삭제
    if image_path.exists():
        os.remove(image_path)  # 파일 삭제
    else:
        raise HTTPException(status_code=404, detail="이미지 파일을 찾을 수 없습니다.")
    
    # 게시글에서 이미지 URL 제거
    board.imgUrl = "string"  # 또는 board.imgUrl = ""로 설정
    session.add(board)
    session.commit()

    return {"detail": f"ID가 {id}인 게시글의 이미지가 삭제되었습니다."}