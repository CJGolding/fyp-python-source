from typing import Optional, Iterable

from common.types import CandidateGame


class MinHeap:
    def __init__(self, iterable: Optional[Iterable[CandidateGame]] = None) -> None:
        """
        Min-Heap data structure for CandidateGame objects with uniqueness constraint on anchor_player (p_i).
        :param iterable: Optional iterable of CandidateGame objects to initialise the heap with.
        """
        self.__heap: list[CandidateGame] = []
        self.__index_map: dict[int, int] = {}
        if iterable:
            for game in iterable:
                self.push(game)

    def __update_existing(self, player_id: int, new_game: CandidateGame) -> None:
        """
        Internal method to update an existing game for an anchor_player.
        :param player_id: The ID of the anchor_player whose game is to be updated.
        :param new_game: The new CandidateGame to replace the existing one (X_i, Y_i).
        """
        index: int = self.__index_map[player_id]
        self.__heap[index] = new_game
        self.__update_position(index)

    def __remove_at_index(self, index: int) -> None:
        """
        Internal method to remove a game at a specific index.
        :param index: The index of the game to remove.
        """
        last_index: int = len(self.__heap) - 1

        if index == last_index:
            game: CandidateGame = self.__heap.pop()
            del self.__index_map[game.anchor_player.id]
            return

        self.__swap(index, last_index)

        removed_game: CandidateGame = self.__heap.pop()
        del self.__index_map[removed_game.anchor_player.id]

        self.__update_position(index)

    def __update_position(self, index: int) -> None:
        """
        Internal method to update the position of a game after modification.
        :param index: The index of the game to update.
        """
        if index == 0:
            self.__sift_down(index)
            return

        parent_index: int = (index - 1) // 2
        if self.__heap[index] < self.__heap[parent_index]:
            self.__sift_up(index)
        else:
            self.__sift_down(index)

    def __sift_up(self, index: int) -> None:
        """
        Internal method to sift up a game to maintain the heap invariant.
        :param index: The index of the game to sift up.
        """
        while index > 0:
            parent_index: int = (index - 1) // 2
            if self.__heap[index] < self.__heap[parent_index]:
                self.__swap(index, parent_index)
                index = parent_index
            else:
                break

    def __sift_down(self, index: int) -> None:
        """
        Internal method to sift down a game to maintain the heap invariant.
        :param index: The index of the game to sift down.
        """
        size: int = len(self.__heap)
        while True:
            smallest: int = index
            left: int = 2 * index + 1
            right: int = 2 * index + 2

            if left < size and self.__heap[left] < self.__heap[smallest]:
                smallest = left
            if right < size and self.__heap[right] < self.__heap[smallest]:
                smallest = right

            if smallest != index:
                self.__swap(index, smallest)
                index = smallest
            else:
                break

    def __swap(self, i: int, j: int) -> None:
        """
        Internal method to swap two games in the heap and update the index map.
        :param i: The index of the first game.
        :param j: The index of the second game.
        """
        self.__heap[i], self.__heap[j] = self.__heap[j], self.__heap[i]
        self.__index_map[self.__heap[i].anchor_player.id] = i
        self.__index_map[self.__heap[j].anchor_player.id] = j

    def __len__(self) -> int:
        return len(self.__heap)

    def __str__(self) -> str:
        return str(self.__heap)

    def __getitem__(self, index: int) -> Optional[CandidateGame]:
        """Returns the game at a specific index. This enables direct indexing."""
        return self.__heap[index]

    def __contains__(self, player_id: int) -> bool:
        """Checks if a game for a specific anchor_player ID exists in the heap."""
        return player_id in self.__index_map

    def peek(self) -> Optional[CandidateGame]:
        """
        Returns the game with the lowest priority without removing it.
        Time Complexity: O(1)
        :return: The CandidateGame with the lowest priority, or None if the heap is empty.
        """
        if not self.__heap:
            return None
        return self.__heap[0]

    def push(self, game: CandidateGame) -> None:
        """
        Inserts a game or updates it if the anchor_player already has a game in the heap.
        Enforces uniqueness such that there is only one game per anchor_player.
        Time Complexity: O(log n)
        :param game: The CandidateGame to insert or update (X_i, Y_i).
        """
        player_id: int = game.anchor_player.id
        if player_id in self.__index_map:
            self.__update_existing(player_id, game)
        else:
            self.__heap.append(game)
            index: int = len(self.__heap) - 1
            self.__index_map[player_id] = index
            self.__sift_up(index)

    def remove(self, player_id: int) -> None:
        """
        Removes a specific anchor_player's game from the heap using their player ID.
        Time Complexity: O(log n)
        :param player_id: The ID of the anchor_player whose game is to be removed.
        """
        if player_id in self.__index_map:
            self.__remove_at_index(self.__index_map[player_id])

    def index(self, player_id: int) -> int:
        """
        Returns the index of a specific anchor_player's game in the heap using their player ID.
        Time Complexity: O(1)
        :param player_id: The ID of the anchor_player whose game index is to be retrieved.
        :return: The index of the anchor_player's game, or -1 if not found.
        """
        return self.__index_map.get(player_id, -1)
