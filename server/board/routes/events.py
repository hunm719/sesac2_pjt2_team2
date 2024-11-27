from fastapi import APIRouter, HTTPException, status, Body, Depends
from typing import List
from board.database.connection import get_session
from sqlmodel import select, Session
from board.models.events import Board, BoardUpdate, Comment
from sqlalchemy.orm import joinedload
from fastapi.encoders import jsonable_encoder

board_router = APIRouter()


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


# 게시글 등록 => POST /board/ => create_board()
@board_router.post("/", status_code=status.HTTP_201_CREATED)
def create_board(data: Board = Body(...), session=Depends(get_session)) -> dict:
    session.add(data)  # 데이터베이스에 데이터를 추가
    session.commit()  # 변경사항을 저장
    session.refresh(data)  # 최신 데이터로 갱신
    return {"message": "게시글이 정상적으로 등록되었습니다."}


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
