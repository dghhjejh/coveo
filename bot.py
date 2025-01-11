import random
from game_message import *


import random
from game_message import *


class Bot:
    def __init__(self):
        print("Initializing your super mega duper bot")

    def sortedItems(self, game_message: TeamGameState):
        """
        Trie les items en deux catégories : négatifs dans notre zone et positifs hors de notre zone
        """
        negativeItems = []
        positiveItems = []
        zone_positions = {(pos.x, pos.y) for pos in self.analyze_team_zone(game_message)}

        for item in game_message.items:
            item_pos = (item.position.x, item.position.y)
            if item.type in ["radiant_slag", "radiant_core"]:
                if item_pos in zone_positions:
                    negativeItems.append(item)
            else:
                if item_pos not in zone_positions:
                    positiveItems.append(item)

        return (negativeItems, positiveItems)
    

    def placeToDropPositiveItem(self, game_message: TeamGameState) -> Optional[Position]:
        """
        Trouve une position vide dans notre zone pour déposer un item positif.
        Returns:
            Optional[Position]: Position où déposer l'item ou None si aucune position n'est disponible
        """
        # Récupère toutes les positions de notre zone
        zone_positions = self.analyze_team_zone(game_message)

        #Créer un ensemble des positions des items pour une recherche efficace
        item_positions = {(item.position.x, item.position.y) for item in game_message.items}

        #Créer un ensemble des positions des personnages
        character_positions = {(char.position.x, char.position.y) 
                            for char in game_message.yourCharacters + game_message.otherCharacters 
                            if char.alive}

        #Parcourir toutes les positions de notre zone
        for pos in zone_positions:
            # Vérifier si la position est vide (pas de mur, pas d'item, pas de personnage)
            if (game_message.map.tiles[pos.y][pos.x] == TileType.EMPTY and 
                (pos.x, pos.y) not in item_positions and 
                (pos.x, pos.y) not in character_positions):
                return pos

        return None

    def placeToDropNegativeItem(self, game_message: TeamGameState):
        """
        Trouve une position hors de notre zone pour déposer un item négatif.
        Returns a Position object representing where to drop the negative item.
        """
        our_zone_positions = self.analyze_team_zone(game_message)
        our_zone_coords = set((pos.x, pos.y) for pos in our_zone_positions)

        #Look for an accessible position just outside our zone
        for zone_pos in our_zone_positions:
            # Check adjacent positions (up, right, down, left)
            adjacent_positions = [
                Position(zone_pos.x, zone_pos.y - 1),  # up
                Position(zone_pos.x + 1, zone_pos.y),  # right
                Position(zone_pos.x, zone_pos.y + 1),  # down
                Position(zone_pos.x - 1, zone_pos.y)   # left
            ]
            for pos in adjacent_positions:
                # Check if position is valid (within map bounds and not a wall)
                if (0 <= pos.x < game_message.map.width and 
                    0 <= pos.y < game_message.map.height and 
                    game_message.map.tiles[pos.y][pos.x] != TileType.WALL and
                    (pos.x, pos.y) not in our_zone_coords):
                    return pos

        return None

    def InTeamZone(self, character: Character):
        if character.alive == True:
            for zonePos in self.analyze_team_zone():
                if character.position.x == zonePos.x and character.position.y == zonePos.y:
                    return True
        return False
        
        

    def attack(self, character: Character, game_message: TeamGameState):
        """
        Simple attack strategy with checks for valid positions
        """
        actions = []
        
        if not character.alive:
            return actions

        zone_positions = self.analyze_team_zone(game_message)

        # Helper function to check if a position is a wall
        def is_wall(pos):
            return game_message.map.tiles[pos.y][pos.x] == TileType.WALL

        # If carrying an item
        if character.carriedItems:
            item = character.carriedItems[0]
            # Handle positive item
            if item.value > 0:
                # Drop in our zone if we're there
                if any(character.position.x == pos.x and character.position.y == pos.y for pos in zone_positions):
                    actions.append(DropAction(characterId=character.id))
                # Move to our zone
                else:
                    # Find first non-wall position in our zone
                    for pos in zone_positions:
                        if not is_wall(pos):
                            actions.append(MoveToAction(characterId=character.id, position=pos))
                            break
            # Handle negative item
            else:
                # Drop if we're outside our zone
                if not any(character.position.x == pos.x and character.position.y == pos.y for pos in zone_positions):
                    actions.append(DropAction(characterId=character.id))
                # Move outside our zone
                else:
                    # Find first valid position outside zone
                    for y in range(len(game_message.teamZoneGrid)):
                        for x in range(len(game_message.teamZoneGrid[0])):
                            pos = Position(x, y)
                            if not is_wall(pos) and not any(pos.x == zp.x and pos.y == zp.y for zp in zone_positions):
                                actions.append(MoveToAction(characterId=character.id, position=pos))
                                return actions

        # If not carrying anything
        else:
            # First priority: grab negative items from our zone
            for item in game_message.items:
                if item.value < 0:
                    # Check if item is in our zone and not in a wall
                    if any(item.position.x == pos.x and item.position.y == pos.y for pos in zone_positions) and not is_wall(item.position):
                        # If we're at item position, grab it
                        if character.position.x == item.position.x and character.position.y == item.position.y:
                            actions.append(GrabAction(characterId=character.id))
                            break
                        # Otherwise move to it
                        else:
                            actions.append(MoveToAction(characterId=character.id, position=item.position))
                            break
            
            # Second priority: if no negative items in our zone, look for positive items outside
            if not actions:
                for item in game_message.items:
                    if item.value > 0:
                        # Check if item is outside our zone and not in a wall
                        if not any(item.position.x == pos.x and item.position.y == pos.y for pos in zone_positions) and not is_wall(item.position):
                            # If we're at item position, grab it
                            if character.position.x == item.position.x and character.position.y == item.position.y:
                                actions.append(GrabAction(characterId=character.id))
                                break
                            # Otherwise move to it
                            else:
                                actions.append(MoveToAction(characterId=character.id, position=item.position))
                                break

        return actions

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

        def is_wall(pos):
            return game_message.map.tiles[pos.y][pos.x] == TileType.WALL

        if defender.alive:
            # First check if there are enemies carrying our positive items
            for character in game_message.otherCharacters:
                if character.alive and character.carriedItems:
                    for item in character.carriedItems:
                        if item.value > 0:
                            if not is_wall(character.position):
                                actions.append(
                                    MoveToAction(
                                        characterId=defender.id, 
                                        position=character.position
                                    )
                                )
                                return actions

            # Then check for enemies in our zone
            for character in game_message.otherCharacters:
                if character.alive:
                    for zonePos in zonePositions:
                        if character.position.x == zonePos.x and character.position.y == zonePos.y:
                            if not is_wall(character.position):
                                actions.append(
                                    MoveToAction(
                                        characterId=defender.id, 
                                        position=character.position
                                    )
                                )
                                return actions
                            
            # Default to center position
            if zonePositions:
                valid_positions = [pos for pos in zonePositions if not is_wall(pos)]
                if valid_positions:
                    center_pos = valid_positions[len(valid_positions) // 2]
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

        # Handle other characters with random moves (skip the defender)
        if len(game_message.yourCharacters) > 1:
            defender_actions = self.get_defender_move(game_message)
            actions.extend(defender_actions)
            for character in game_message.yourCharacters[1:]:  # Start from index 1 to skip defender
                #actions.append(self.attack(character, game_message))
               actions.extend(self.attack(character, game_message))
        else:
           actions.extend(self.attack(character, game_message))
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
    
    def near_items(self, character: Character, game_message: TeamGameState) -> tuple[Optional[Item], Optional[Item]]:
        """
        Trouve les items négatifs et positifs les plus proches qui sont accessibles
        """
        negativeItems, positiveItems = self.sortedItems(game_message)

        """if not character.alive:
            return None, None

        min_dist_neg = float('inf')
        min_dist_pos = float('inf')
        nearest_neg = None
        nearest_pos = None

        for item in negativeItems:
            dist = self.distance(character.position, item.position, game_message.map)
            if dist < min_dist_neg:
                min_dist_neg = dist
                nearest_neg = item

        for item in positiveItems:
            dist = self.distance(character.position, item.position, game_message.map)
            if dist < min_dist_pos:
                min_dist_pos = dist
                nearest_pos = item"""
        return negativeItems[0], positiveItems[0]
        #return nearest_neg, nearest_pos

