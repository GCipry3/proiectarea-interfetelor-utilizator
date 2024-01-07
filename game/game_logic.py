from .player import Player
from .enemy import Enemy
from .super_enemy import SuperEnemy
from .projectile import Projectile
from env.config import SCREEN_WIDTH, SCREEN_HEIGHT, ENEMY_WIDTH, ENEMY_HEIGHT, ENEMY_COUNT
from .score_board import ScoreBoard
import sys

class GameLogic:
    """
    The GameLogic class represents the logic and mechanics of the game.
    It handles the player, enemies, and projectile collisions.

    Attributes:
        player (Player): The player object.
        enemies (list[Enemy]): The list of enemy objects.
    """

    def __init__(self):
        self.player = None
        self.enemies:list[Enemy] = []
        self.enemies_projectiles: list[Projectile] = []
        self.enemies_thighs: list[Projectile] = []
        self.score_board = ScoreBoard()

        self.start_game()

    def start_game(self):
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - ENEMY_HEIGHT)

        gap = SCREEN_WIDTH // ENEMY_COUNT
        for i in range(ENEMY_COUNT):
            self.enemies.append(Enemy(i * gap, 100))

    def check_next_level(self):
        '''
        Checks if the player has killed all the enemies.
        '''
        if not self.enemies:
            self.next_level()
    
    def check_game_over(self):
        '''
        Checks if the player has no lives left.
        '''
        return self.player.lives == 0

    def update(self):
        """
        Updates the game logic.
        It updates the player and enemies, and checks for collisions.
        Returns:
            True: If the game is still running.
            False: If the game is over.
        """
        self.player.update()
        self.update_enemy()
        self.update_enemy_projectiles()
        self.update_enemy_thighs()

        self.check_player_projectile_collisions()
        self.check_enemy_projectile_collisions()
        self.check_enemy_collisions()
        self.check_player_collisions()

        self.check_next_level()

        if self.check_game_over():
            return False

        return True

    def update_enemy(self):
        '''
        Update the enemy projectiles list.
        '''
        for enemy in self.enemies:
            if enemy.lives <= 0:
                self.enemies_thighs.extend(enemy.drop_thigh())
                
                self.score_board.chicken_kills += 1
                self.enemies.remove(enemy)
            else:
                enemy.update()
                projectile = enemy.shoot()
                if projectile:
                    self.enemies_projectiles.append(projectile)

    def next_level(self):
        self.score_board.level += 1

        # Generate the enemies
        nr_of_enemies = ENEMY_COUNT + self.score_board.level // 2
        gap = SCREEN_WIDTH // nr_of_enemies
        for i in range(nr_of_enemies):
            self.enemies.append(Enemy(i * gap, 100))

        # Generate the super enemies
        nr_of_super_enemies = self.score_board.level
        gap = SCREEN_WIDTH // nr_of_super_enemies
        for i in range(self.score_board.level):
            self.enemies.append(SuperEnemy(i * gap, 100))
        
        self.enemies_projectiles: list[Projectile] = []

    def update_enemy_projectiles(self):
        '''
        Updates the position of the enemy's projectiles.
        Removes projectiles that have reached the bottom of the screen.
        '''
        for projectile in self.enemies_projectiles:
            projectile.update()
            if projectile.y > SCREEN_HEIGHT:
                self.enemies_projectiles.remove(projectile)

    def update_enemy_thighs(self):
        '''
        Updates the position of the enemy's thighs.
        Removes thighs that have reached the bottom of the screen.
        '''
        for thigh in self.enemies_thighs:
            thigh.update()
            if thigh.y > SCREEN_HEIGHT:
                self.enemies_thighs.remove(thigh)

    def check_player_projectile_collisions(self):
        '''
        Checks for collisions between the player's projectiles and the enemies.
        Removes the projectiles and enemies that have collided.
        '''
        for projectile in self.player.projectiles:
            for enemy in self.enemies:
                if projectile.check_collision(enemy):
                    self.player.projectiles.remove(projectile)
                    enemy.lives -= 1
                    break
        
        for projectile in self.player.projectiles:
            for enemy_projectile in self.enemies_projectiles:
                if projectile.check_collision(enemy_projectile):
                    self.player.projectiles.remove(projectile)
                    self.enemies_projectiles.remove(enemy_projectile)
                    break
    
    def check_enemy_projectile_collisions(self):
        '''
        Checks for collisions between the enemy's projectiles and the player.
        Removes the projectiles that have collided.
        '''
        for projectile in self.enemies_projectiles:
            if projectile.check_collision(self.player):
                self.enemies_projectiles.remove(projectile)
                self.player.lives -= 1
    
    def check_enemy_collisions(self):
        '''
        Checks for collisions between the enemies and the player.
        Removes the enemies that have collided.
        '''
        for enemy in self.enemies:
            if enemy.check_collision(self.player):
                self.enemies.remove(enemy)
                self.player.lives -= 1
    
    def check_player_collisions(self):
        '''
        Checks for collisions between the player and the thighs.
        Removes the thighs that have collided and update the score_board.
        '''
        for thigh in self.enemies_thighs:
            if thigh.check_collision(self.player):
                self.enemies_thighs.remove(thigh)
                self.score_board.collected_thighs += 1
                break