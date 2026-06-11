from __future__ import annotations

from copy import deepcopy
from typing import Literal, TypedDict
from uuid import uuid4


Role = Literal["system", "user", "assistant"]


class Message(TypedDict):
    role: Role
    content: str


# 면접 세션별 메시지 이력 저장소
sessions: dict[str, list[Message]] = {}

# 면접 세션별 면접관 유형 저장소
session_roles: dict[str, str] = {}


def create_session(role: str = "general") -> str:
    """
    새 UUID 면접 세션 ID를 만들고 빈 메시지 목록과 면접관 유형을 등록합니다.

    힌트:
    - str(uuid4()) 로 session_id 를 만든다.
    - sessions[session_id] = [] 로 빈 목록을 등록한다.
    - session_roles[session_id] = role 로 면접관 유형을 저장한다.
    - session_id 를 반환한다.
    """
    # 여기에 코드를 채워요.
    session_id = str(uuid4()) # TODO: str(uuid4())
    sessions[session_id] = []  # TODO: []
    session_roles[session_id] = role # TODO: role
    return session_id


def add_message(session_id: str, role: Role, content: str) -> None:
    """
    지정한 세션에 role/content 메시지를 순서대로 추가합니다.

    힌트:
    - session_id 가 sessions 에 없으면 KeyError 를 발생시킨다.
    - sessions[session_id].append({"role": role, "content": content}) 로 추가한다.
    """
    if session_id not in sessions:
        # 여기에 KeyError 를 발생시키는 코드를 채워요.
        raise KeyError(f"unknown session_id: {session_id}")  # TODO: KeyError(f"unknown session_id: {session_id}")

    sessions[session_id].append({"role": role, "content": content})


def get_history(session_id: str) -> list[Message]:
    """
    세션별 메시지 이력을 복사본으로 반환합니다.

    힌트:
    - session_id 가 없으면 KeyError.
    - deepcopy(sessions[session_id]) 를 반환한다.
    """
    if session_id not in sessions:
        raise KeyError(f"unknown session_id: {session_id}")

    # 여기에 deepcopy 반환 코드를 채워요.
    return  deepcopy(sessions[session_id]) # TODO: deepcopy(sessions[session_id])


def get_session_role(session_id: str) -> str:
    """세션의 현재 면접관 유형을 반환합니다."""
    return session_roles.get(session_id, "general")


def set_session_role(session_id: str, role: str) -> None:
    """
    세션의 면접관 유형을 변경합니다.

    힌트:
    - session_id 가 없으면 KeyError.
    - session_roles[session_id] = role 로 업데이트한다.
    """
    if session_id not in sessions:
        raise KeyError(f"unknown session_id: {session_id}")

    # 여기에 session_roles 업데이트 코드를 채워요.
    session_roles[session_id] = role # TODO: role


def clear_session(session_id: str) -> None:
    """세션은 유지하고 메시지 이력만 초기화합니다."""
    if session_id not in sessions:
        raise KeyError(f"unknown session_id: {session_id}")

    sessions[session_id] = []
