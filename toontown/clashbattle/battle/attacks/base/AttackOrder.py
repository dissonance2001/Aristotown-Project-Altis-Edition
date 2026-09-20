from operator import attrgetter
from typing import List

from toontown.clashbattle.battle.BattleAvatar import BattleAvatar
from toontown.clashbattle.battle.attacks.server.AttackAI import AttackAI
from toontown.clashbattle.battle.attacks.server.toon.ToonAttackAI import ToonAttackAI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class AttackOrder:
    """AttackOrder: Manages the order of attacks of a given battle
    round, as well as keeping track of the current attack index.
    """

    __slots__ = ("_attackIndex", "_attacks", "currentAttack")
    
    def __init__(self) -> None:
        self._attackIndex = -1
        self._attacks = []  # type: list[AttackAI]
        self.currentAttack = None
    
    def __next__(self) -> AttackAI:
        if self.reachedEnd():
            return

        self.attackIndex += 1
        self.currentAttack = self._attacks[self.attackIndex]
        return self.currentAttack
    
    def __repr__(self) -> str:
        basestr = f"AttackOrder(attackIndex={self.attackIndex})\n"
        for attack in self.getAttacks():
            basestr += f"{repr(attack)},\n"
        return basestr
    
    def __getitem__(self, attackIndex: int) -> AttackAI:
        return self._attacks[attackIndex]
    
    def getCurrentAttack(self) -> AttackAI:
        return self._attacks[self.attackIndex]
    
    def reachedEnd(self) -> bool:
        return self.attackIndex >= len(self._attacks) - 1

    def cleanup(self) -> None:
        self.currentAttack = None

        for attack in self._attacks:
            attack.cleanup()

        self.setAttacks([])

    def insert(self, index: int, attack: AttackAI, overrideInserted=None) -> None:
        # Insert the new attack.
        self._attacks.insert(index, attack)

        # Sort the attacks by priority.
        self.sort()

        # Set the inserted flag to True.
        # Also respect an override inserted flag if we have it
        # Override inserted will be None if it doesnt apply, else True/False if it does apply.
        attack.inserted = overrideInserted if overrideInserted is not None else True

    def extend(self, attacks: list) -> None:
        self._attacks.extend(attacks)
    
    def remove(self, attack: AttackAI) -> None:
        if attack in self._attacks:
            self._attacks.remove(attack)
            attack.cleanup()
        else:
            self.notify.warning("Attempted to remove non-existant attack in attack order.")
    
    def append(self, attack: AttackAI, overrideInserted=None) -> None:
        self._attacks.append(attack)

        # Sort the attacks by priority.
        self.sort()

        # Set the inserted flag to True.
        # Also respect an override inserted flag if we have it
        # Override inserted will be None if it doesnt apply, else True/False if it does apply.
        attack.inserted = overrideInserted if overrideInserted is not None else True
    
    def replaceCurrent(self, newAttack: AttackAI) -> None:
        # Cleanup the new attack.
        attack = self.getCurrentAttack()
        attack.cleanup()
        
        # Replace it with the new attack.
        self._attacks[self.attackIndex] = newAttack

    def setAttacks(self, attacks: list) -> None:
        self._attacks = attacks
        self.attackIndex = -1
    
    def getAttacks(self) -> List[AttackAI]:
        return self._attacks

    def sort(self, key=None):
        attackIndex = max(self.attackIndex, 0)
        # If a custom key was provided, sort by that first.
        if key is not None:
            self._attacks[attackIndex:] = sorted(self._attacks[attackIndex:], key=key)

        # Sort all of the attacks which have yet to be calculated based on the
        # priority value that was assigned to it. The higher the priority value,
        # the later it gets calculated.
        self._attacks[attackIndex:] = sorted(self._attacks[attackIndex:], key=attrgetter("priority"))
        
    def getNextAvailableIndex(self) -> int:
        """Finds the next available attack index to insert an attack into. This
        prevents an attack from being inserted into the middle of an attack chain.
        """
        attacks = self.getAttacks()
        index = self.attackIndex

        for attack in attacks[self.attackIndex:]:
            nextAttack = attacks[min(index + 1, len(attacks) - 1)]
            # This attack is part of a chain, see if it's the end of the chain
            # or attack order.
            if isinstance(attack, ToonAttackAI):
                if nextAttack is attack or nextAttack.attackType != attack.attackType:
                    return index
            # This attack isn't part of a chain, just return this index.
            else:
                return index
            
            # Increment the index.
            index += 1

        # This is merely a fallback.
        return self.attackIndex

    def getNextIndexOfTrack(self, track):
        """
        Finds the closest index of the given toon track.
        """

        indices = self.getAllIndicesOfTrack(track)
        if len(indices) <= 0:
            return None

        return indices[0]

    def getAllIndicesOfTrack(self, track):
        """
        Finds all indices that the given toon track occupies.
        """

        attacks = self.getAttacks()
        index = max(self.attackIndex, 0)

        indices = []
        for attack in attacks[index:]:
            if isinstance(attack, ToonAttackAI) and attack.attackType == track:
                indices.append(index)

            index += 1

        return indices

    def getAttacksOfInvoker(self, invoker: BattleAvatar) -> List[AttackAI]:
        return [attack for attack in self.getAttacks() if attack.invoker is invoker]

    def hasAttackOfType(self, attackType):
        attacks = self.getAttacks()
        index = max(self.attackIndex, 0)

        for attack in attacks[index:]:
            if attack.attackType == attackType:
                return True

        return False

    def getAttackOfType(self, attackType):
        attacks = self.getAttacks()
        index = max(self.attackIndex, 0)

        for attack in attacks[index:]:
            if attack.attackType == attackType:
                return attack

        return None

    @property
    def attackIndex(self) -> int:
        return self._attackIndex
    
    @attackIndex.setter
    def attackIndex(self, attackIndex: int) -> None:
        self._attackIndex = attackIndex
