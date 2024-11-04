from pydantic import BaseModel, Field


class RoleCreate(BaseModel):

    name: str = Field(..., max_length=36)
    role_create: bool = False
    role_level: int
    ban: bool = False
    unban: bool = False
    warn: bool = False
    mute: bool = False
    unmute: bool = False
    user_get: bool = False
    user_update: bool = False
    user_delete: bool = False
    user_settings_get: bool = False
    user_settings_update: bool = False
    user_statistics_get: bool = False
    user_statistics_update: bool = False
    friends_create: bool = False
    friends_get: bool = False
    friends_update: bool = False
    friends_delete: bool = False
    games_create: bool = False
    games_get: bool = False
    games_update: bool = False
    games_delete: bool = False
    moves_create: bool = False
    moves_get: bool = False
    moves_update: bool = False
    moves_delete: bool = False
    profile_create: bool = False
    profile_get: bool = False
    profile_update: bool = False
    profile_delete: bool = False
    tournament_registration_create: bool = False
    tournament_registration_get: bool = False
    tournament_registration_update: bool = False
    tournament_registration_delete: bool = False
    tournament_create: bool = False
    tournament_get: bool = False
    tournament_update: bool = False
    tournament_delete: bool = False
