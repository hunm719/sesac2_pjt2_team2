from fastapi import HTTPException, status
from board.models.roles import Role

class Permission:
    @staticmethod
    def check_permission(user_role: Role, allowed_roles: list) -> None:
        """공통 권한 검사 메서드"""
        if user_role not in allowed_roles:
            if user_role == Role.guest:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="로그인이 필요한 기능입니다."
                )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="권한이 없습니다."
            )

    @staticmethod
    def can_edit_post(user_role: Role) -> bool:
        """게시글 작성 권한"""
        Permission.check_permission(user_role, [Role.user, Role.admin])
        return True

    @staticmethod
    def can_view_post(user_role: Role) -> bool:
        """게시글 조회 권한"""
        Permission.check_permission(user_role, [Role.guest, Role.user, Role.admin])
        return True

    @staticmethod
    def can_update_post(user_role: Role, post_owner_id: int, user_id: int) -> bool:
        """게시글 수정 권한"""
        if user_role == Role.admin:
            return True
        if user_role == Role.user and post_owner_id == user_id:
            return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="이 게시글을 수정할 권한이 없습니다."
        )

    @staticmethod
    def can_delete_post(user_role: Role, post_owner_id: int, user_id: int) -> bool:
        """게시글 삭제 권한"""
        if user_role == Role.admin:
            return True
        if user_role == Role.user and post_owner_id == user_id:
            return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="이 게시글을 삭제할 권한이 없습니다."
        )

    @staticmethod
    def can_signin_user(user_role: Role) -> bool:
        """유저 생성 권한"""
        Permission.check_permission(user_role, [Role.guest, Role.admin])
        return True

    @staticmethod
    def can_view_user(user_role: Role) -> bool:
        """유저 조회 권한"""
        Permission.check_permission(user_role, [Role.guest, Role.user, Role.admin])
        return True

    @staticmethod
    def can_update_user(user_role: Role, user_id: int, target_user_id: int) -> bool:
        """유저 정보 수정 권한"""
        if user_role == Role.admin:
            return True
        if user_role == Role.user and user_id == target_user_id:
            return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="유저 정보를 수정할 권한이 없습니다."
        )

    @staticmethod
    def can_delete_user(user_role: Role, user_id: int, target_user_id: int) -> bool:
        """유저 삭제 권한"""
        if user_role == Role.admin:
            return True
        if user_role == Role.user and user_id == target_user_id:
            return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="유저 정보를 삭제할 권한이 없습니다."
        )
