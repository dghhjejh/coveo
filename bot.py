import random
from game_message import *


class Bot:
    def __init__(self):
        print("Initializing your super mega duper bot")

    def analyze_team_zone(self, game_message: TeamGameState):
        """
        Analyze the team zone grid to find the boundaries of our zone
        """
        our_team_id = game_message.currentTeamId
        zone_positions = []
        
        # Loop through the grid to find all positions in our zone
        height = len(game_message.teamZoneGrid)
        width = len(game_message.teamZoneGrid[0])
        
        for y in range(height):
            for x in range(width):
                if game_message.teamZoneGrid[y][x] == our_team_id:
                    zone_positions.append(Position(x, y))
        
        # Print for debugging
        print(f"Found {len(zone_positions)} positions in our zone")
        if zone_positions:
            # Calculate boundaries
            x_coords = [pos.x for pos in zone_positions]
            y_coords = [pos.y for pos in zone_positions]
            min_x = min(x_coords)
            max_x = max(x_coords)
            min_y = min(y_coords)
            max_y = max(y_coords)
            print(f"Zone boundaries: ({min_x},{min_y}) to ({max_x},{max_y})")
        
        return zone_positions

    def get_defender_move(self, game_message: TeamGameState):
        actions = []
        zonePositions = self.analyze_team_zone(game_message)
        defender = game_message.yourCharacters[0]
        if defender.alive == True:
            for character in game_message.otherCharacters:
                # Check if any position in our zone matches the character's position
                if character.alive == True:
                    for zonePos in zonePositions:
                        if character.position.x == zonePos.x and character.position.y == zonePos.y:
                            actions.append(
                                MoveToAction(
                                    characterId=defender.id, 
                                    position=Position(character.position.x, character.position.y)
                                )
                            )
                            return actions  # Return as soon as we find an enemy to chase
                        
        # If no enemies found in our zone, maybe add default position for defender
        if zonePositions:  # If we have at least one zone position
            # Move to middle of our zone if no enemies found
            center_pos = zonePositions[len(zonePositions) // 2]
            actions.append(
                MoveToAction(
                    characterId=defender.id,
                    position=center_pos
                )
            )
        
        return actions
    
    def get_next_move(self, game_message: TeamGameState):
        """
        Here is where the magic happens, combining defender moves with other character moves
        """
        actions = []

        # Get defender moves first
        defender_actions = self.get_defender_move(game_message)
        actions.extend(defender_actions)

        # Handle other characters with random moves (skip the defender)
        for character in game_message.yourCharacters[1:]:  # Start from index 1 to skip defender
            actions.append(
                random.choice([
                    MoveUpAction(characterId=character.id),
                    MoveRightAction(characterId=character.id),
                    MoveDownAction(characterId=character.id),
                    MoveLeftAction(characterId=character.id),
                    GrabAction(characterId=character.id),
                    DropAction(characterId=character.id),
                ])
            )
        
        return actions
    
    def distance(pos1: Position, pos2: Position, game_map: GameMap) -> int:
        """
        Calcule la distance réelle (en évitant les murs) entre deux positions
        Retourne float('inf') si aucun chemin n'existe
        """
        from collections import deque
        
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        queue = deque([(pos1, 0)])
        visited = set([(pos1.x, pos1.y)])
        
        while queue:
            current_pos, dist = queue.popleft()
            
            if current_pos.x == pos2.x and current_pos.y == pos2.y:
                return dist
                
            for dx, dy in directions:
                new_x = current_pos.x + dx
                new_y = current_pos.y + dy
                
                if (0 <= new_x < game_map.width and 
                    0 <= new_y < game_map.height and 
                    game_map.tiles[new_y][new_x] != TileType.WALL and
                    (new_x, new_y) not in visited):
                    
                    visited.add((new_x, new_y))
                    queue.append((Position(new_x, new_y), dist + 1))
        
        return float('inf')
    
    def near_items(character: Character, negativeItems: list[Item], positiveItems: list[Item], game_map: GameMap) -> tuple[Optional[Item], Optional[Item]]:
        """
        Trouve les items négatifs et positifs les plus proches qui sont accessibles
        """
        if not character.alive:
            return None, None
            
        min_dist_neg = float('inf')
        min_dist_pos = float('inf')
        nearest_neg = None
        nearest_pos = None
        
        for item in negativeItems:
            dist = distance(character.position, item.position, game_map)
            if dist < min_dist_neg:
                min_dist_neg = dist
                nearest_neg = item
                
        for item in positiveItems:
            dist = distance(character.position, item.position, game_map)
            if dist < min_dist_pos:
                min_dist_pos = dist
                nearest_pos = item
        
        return nearest_neg, nearest_pos

