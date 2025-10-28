# backend/constants/events.py

class ClientEvents:
    JOIN_GAME = "join_game"
    LEAVE_GAME = "leave_game"
    SEND_ANSWER = "send_answer"
    REQUEST_UPDATE = "request_update"


class ServerEvents:
    PLAYER_JOINED = "player_joined"
    PLAYER_LEFT = "player_left"
    GAME_UPDATED = "game_updated"
    NEW_ANSWER = "new_answer"
    ERROR = "error"
