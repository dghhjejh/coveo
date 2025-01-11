import random
from game_message import *


class Bot:
    def __init__(self):
        print("Initializing your super mega duper bot")

    def sortedItems(self, items: TeamGameState.items):
        negativeItems = []
        positiveItems = []
        
        for i in items:
            if (i.type == "radiant_slag" or i.type == "radiant_core") :
                if i.position in analyze_team_zone () :
                    negativeItems.append(i)
            else :
                if (not i.position in analyze_team_zone() ) :
                    positiveItems.append(i)

        return (negativeItems, positiveItems)
    
    def nearItems(self, character: Character):
        """
            retourne l'item negative la plus proche dans la zone(None s'il n'y en a pas)
            et l'item positive la plus proche hors de la zone(None s'il n'y en a pas)
        """
        pass


    def placeToDropPositiveItem(self):
        pass

    def placeToDropNegativeItem(self, game_message: TeamGameState):
        """
        Trouve une position hors de notre zone pour déposer un item négatif.
        Returns a Position object representing where to drop the negative item.
        """
        our_zone_positions = self.analyze_team_zone(game_message)
        our_zone_coords = set((pos.x, pos.y) for pos in our_zone_positions)
        
        # Look for an accessible position just outside our zone
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
        
        

    def attack(self, character: Character): 
        (negativeItem, positionItem) = sortedItems() #nearItems(character.position)
        
        if len(character.carriedItems) > 0: #si j'ai un item

            if character.carriedItems[0] > 0: # si l'item est positive

                if character.position == placeToDropPositiveItem(): #quand j'arrive à la position
                    return DropAction(characterId=character.id)
                else:
                    return MoveToAction(characterId=character.id, position= placeToDropPositiveItem())
            
            else: # si l'item est negative

                if character.position == placeToDropNegativeItem(): #quand j'arrive à la position
                    return DropAction(characterId=character.id)
                else:
                    return MoveToAction(characterId= character.id, position= placeToDropNegativeItem())
                pass
        else: #si je n'ai pas d'item
            if InTeamZone() and negativeItem[0].position: #si je suis dans notre zone et qu'il y un item negative

                if character.position == negativeItem[0].position:#quand j'arrive à la position
                    return GrabAction(characterId=character.id)
                
                else:
                    return MoveToAction(characterId=character.id, position= negativeItem[0].position)
                
            elif positionItem[0].position: #s'il y a un item positive hors de notre zone

                if character.position == positionItem[0].position:#quand j'arrive à la position
                    return GrabAction(characterId=character.id)
                else:
                    return MoveToAction(characterId=character.id, position=positionItem[0].position)
            """
            else:
                se comporter comme un defender
            """
            

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

        # Handle other characters with random moves (skip the defender)
        if len(game_message.yourCharacters) > 1:
            defender_actions = self.get_defender_move(game_message)
            actions.extend(defender_actions)
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
        else:
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

