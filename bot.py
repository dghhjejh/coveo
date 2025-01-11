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

    def placeToDropNegativeItem(self):
        pass

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

