# backend/constants/events.py

class ClientEvents:
    JOIN_GAME = "join_game"
    LEAVE_GAME = "leave_game"
    SEND_ANSWER = "send_answer"
    REQUEST_UPDATE = "request_update"
    START_GAME = "start_game"
    CHANGE_PHASE = "change_phase"
    CHANGE_QUESTION = "change_question"
    BUZZER_PRESSED = "buzzer_pressed"
    BUZZER_RESET = "buzzer_reset"
    SHOW_FINAL_SCORES = "show_final_scores"


class ServerEvents:
    PLAYER_JOINED = "player_joined"
    PLAYER_LEFT = "player_left"
    GAME_UPDATED = "game_updated"
    PHASE_CHANGED = "phase_changed"
    QUESTION_CHANGED = "question_changed"
    NEW_ANSWER = "new_answer"
    BUZZER_WINNER = "buzzer_winner"
    BUZZER_RESET = "buzzer_reset"
    SHOW_FINAL_SCORES = "show_final_scores"
    
