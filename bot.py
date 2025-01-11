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

    def notreZone():
        pass

    def placeToDropPositiveItem(self):
        pass

    def placeToDropNegativeItem(self):
        pass

    def InTeamZone():
        pass

    def attack(self, character: Character): 
        (negativeItem, positionItem) = sortedItems() #nearItems(character.position)
        
        if len(character.carriedItems) > 0: #si j'ai un item

            if character.carriedItems[0] < 0: # si l'item est positive

                if character.position == placeToDropPositiveItem(): #quand j'arrive à la position
                    DropAction(characterId=character.id)
                else:
                    MoveToAction(characterId=character.id, position= placeToDropPositiveItem())
            
            else: # si l'item est negative

                if character.position == placeToDropNegativeItem(): #quand j'arrive à la position
                    DropAction(characterId=character.id)
                else:
                    MoveToAction(characterId= character.id, position= placeToDropNegativeItem())
                pass
        else: #si je n'ai pas d'item
            if InTeamZone() and negativeItem[0].position: #si je suis dans notre zone et qu'il y un item negative

                if character.position == negativeItem[0].position:#quand j'arrive à la position
                    GrabAction(characterId=character.id)
                
                else:
                    MoveToAction(characterId=character.id, position= negativeItem[0].position)
                
            elif positionItem[0].position: #s'il y a un item positive hors de notre zone

                if character.position == positionItem[0].position:#quand j'arrive à la position
                    GrabAction(characterId=character.id)
                else:
                    MoveToAction(characterId=character.id, position=positionItem[0].position)
            """
            else:
                se comporter comme un defender
            """
            


        

    def get_next_move(self, game_message: TeamGameState):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """
        actions = []

        for character in game_message.yourCharacters:
            actions.append(
                random.choice(
                    [
                        MoveUpAction(characterId=character.id),
                        MoveRightAction(characterId=character.id),
                        MoveDownAction(characterId=character.id),
                        MoveLeftAction(characterId=character.id),
                        GrabAction(characterId=character.id),
                        DropAction(characterId=character.id),
                    ]
                )
            )

        # You can clearly do better than the random actions above! Have fun!
        return actions
