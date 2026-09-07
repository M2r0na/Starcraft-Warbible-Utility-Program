import math

MOBS_PER_WAVE = 5
RESPAWN_TIME = 11.5

def damage(base, bonus, upgrade):
    return base + bonus * upgrade

def attack_speed(stimpack):
    return 0.5 if stimpack else 1.0

def hits(monster_hp, dmg):
    return math.ceil(monster_hp / dmg)

def kill_time(monster_hp, dmg, stimpack):
    return hits(monster_hp, dmg) * attack_speed(stimpack)

def exp_per_hour(monster):
    kills = (3600 / RESPAWN_TIME) * MOBS_PER_WAVE
    return kills * monster["exp"]

def gold_per_hour(monster):
    kills = (3600 / RESPAWN_TIME) * MOBS_PER_WAVE
    return kills * monster["gold"]