import sys
import math

"""
The order in which actions happens in between two rounds is:
   Enemies move towards their targets.
   If a MOVE command was given, Wolff moves towards his target.
   Game over if an enemy is close enough to Wolff.
   If a SHOOT command was given, Wolff shoots an enemy.
   Enemies with zero life points are removed from play.
   Enemies collect data points they share coordinates with.

   MOVE x y or SHOOT id
   step not more than 1000 units
   less than 2000 units to enemy causes death
   enemy moves 500 units, if data close than 500 - its lost

Expert rules:
    When shooting an enemy, the damage dealt is 125 000 divided by x ** 1.2,
    rounded to the nearest integer; x is equal to the Euclidean distance between Wolff and the enemy.
    If several data points tie as the closest to an enemy, that enemy will aim for the data point with the smallest id.
"""


class GameMechanicsHelper:
    global global_data_count, global_data_points, global_enemies, global_player

    @staticmethod
    def distance_to_object(player_, enemy):
        return math.sqrt((player_['x'] - enemy['x']) ** 2 + (player_['y'] - enemy['y']) ** 2)

    def damage_dealt(self, player_, enemy):
        return round(125000 / self.distance_to_object(player_=player_, enemy=enemy) ** 1.2)

    def return_new_pos(self, step, current_pos, target):
        max_dist = self.distance_to_object(current_pos, target)
        delta_dist = step / max_dist
        dx = target['x'] - current_pos['x']
        dy = target['y'] - current_pos['y']
        return round(current_pos['x'] + dx * delta_dist), round(current_pos['y'] + dy * delta_dist)

    def enemy_next_position(self, enemy):
        # find the nearest data
        the_nearest_data = 0
        for i in range(global_data_count):
            if self.distance_to_object(enemy, global_data_points[i]) < self.distance_to_object(enemy, global_data_points[the_nearest_data]):
                the_nearest_data = i
        return self.return_new_pos(500, enemy, global_data_points[the_nearest_data])

    def player_next_position(self, target):
        return self.return_new_pos(1000, global_player, target)


class GameOptimizer:
    global global_data_count, global_data_points, global_enemies, global_player

    def __init__(self):
        self.current_score = 0
        self.predict = 0
        self.kill_price = 10
        self.data_price = 100
        self.shots_current = 0
        self.hp_total = 0
        self.enemies_killed = 0

    def extra_points(self):
        """
        DP * max(0, (L - 3 * S)) * 3, where:
            DP is the number of data points left.
            L is the total amount of life points enemies have among themselves at the start of the game.
            S is the total number of shots fired during play.
        """
        return global_data_count * max(0, (self.hp_total - 3 * self.shots_current)) * 3

    def count_score(self):
        if global_data_count > 0:
            score = global_data_count * 100 + self.enemies_killed * 10
            return score
        else:
            return 0

    def main_optimizer(self):

        next_enemy_step = global_enemies[0]
        next_enemy_step['x'], next_enemy_step['y'] = game_helper.enemy_next_position(global_enemies[0])
        distance_to_target = game_helper.distance_to_object(global_enemies[0], global_data_points[0])
        max_depth = int(distance_to_target // 500)

        # generate all variants
        moves_tree = []
        for i in range(max_depth):
            temp = []
            for k in range(max_depth):
                if k < i:
                    temp.append(0)
                else:
                    temp.append(1)
            moves_tree.append(temp)

        # analisys the best solution
        best_analisys = {'score': 0, 'tree': ''}
        for decision in moves_tree:
            shoots = self.shots_current
            current_enemy_hp = global_enemies[0]['hp']
            player_predict = global_player
            enemy_predict = global_enemies[0]
            fail = False
            for move in decision:
                if move == 0:
                    # move x, y
                    if game_helper.distance_to_object(player_predict, enemy_predict) < 2000:
                        fail = True
                    player_predict['x'], player_predict['y'] = game_helper.return_new_pos(1000, player_predict, global_data_points[0])
                    enemy_predict['x'], enemy_predict['y'] = game_helper.enemy_next_position(enemy_predict)
                else:
                    # shoot id
                    shoots += 1
                    current_enemy_hp -= game_helper.damage_dealt(player_predict, enemy_predict)
                    if current_enemy_hp <= 0:
                        score_move = 100 + 10 + 1 * max(0, (self.hp_total - 3 * shoots)) * 3
                        if (score_move > best_analisys['score']) and not fail:
                            best_analisys['score'] = score_move
                            best_analisys['tree'] = decision

        # debugging values & parameters:
        # print('Current score: %s' % current_score, file=sys.stderr)
        # print('HP_total: %s' % self.hp_total, file=sys.stderr)
        # print('Damage: %s' % current_damage, file=sys.stderr)
        # print('Next x,y of enemy: %s %s' % (next_enemy_step['x'], next_enemy_step['y']), file=sys.stderr)
        print('Distance to target: %s' % distance_to_target, file=sys.stderr)
        print('Moves to target: %s' % max_depth, file=sys.stderr)
        print(best_analisys, file=sys.stderr)

        return best_analisys['tree'][0]


game_helper = GameMechanicsHelper()
optimizer = GameOptimizer()

first_round = True

while True:
    global_data_points = []
    global_enemies = []

    x, y = [int(i) for i in input().split()]  # x.max() = 16000, y.max() = 9000
    global_player = {'x': x, 'y': y}

    global_data_count = int(input())
    for i in range(global_data_count):
        data_id, data_x, data_y = [int(j) for j in input().split()]
        global_data_points.append({'id': data_id, 'x': data_x, 'y': data_y})

    enemy_count = int(input())
    for i in range(enemy_count):
        enemy_id, enemy_x, enemy_y, enemy_life = [int(j) for j in input().split()]
        global_enemies.append({'id': enemy_id, 'x': enemy_x, 'y': enemy_y, 'hp': enemy_life})
        if first_round:
            optimizer.hp_total += enemy_life
        first_round = False

    result = optimizer.main_optimizer()
    if result == 0:
        print('MOVE 8000 4500')
    else:
        print('SHOOT 0')
        optimizer.shots_current += 1

    # To debug: print("Debug messages...", file=sys.stderr)