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
