from typing import Optional, Iterable, Iterator

from common.types import Player


class _TreeNode:
    def __init__(self, player: Player) -> None:
        """
        Internal node class for AVL tree implementation in SortedSet.
        :param player: The Player object stored in this node.
        """
        self.player = player
        self.left = None
        self.right = None
        self.height = 1
        self.size = 1


class SortedSet:
    def __init__(self, iterable: Optional[Iterable[Player]] = None) -> None:
        """
        A sorted set implementation using an AVL tree to maintain sorted order and allow efficient indexing.
        :param iterable: Optional iterable of Player objects to initialise the set.
        """
        self.__root: Optional[_TreeNode] = None
        if iterable:
            for player in iterable:
                self.__root = self.__insert(self.__root, player)

    @staticmethod
    def __get_height(node: Optional[_TreeNode]) -> int:
        """Get the height of a node, returning 0 for None nodes."""
        return node.height if node else 0

    @staticmethod
    def __get_size(node: Optional[_TreeNode]) -> int:
        """Get the size of a node, returning 0 for None nodes."""
        return node.size if node else 0

    @staticmethod
    def __get_min_value_node(node: _TreeNode) -> _TreeNode:
        """Get the node with the minimum value in a subtree (used for deletion)."""
        current: _TreeNode = node
        while current.left:
            current = current.left
        return current

    def __get_balance(self, node: _TreeNode) -> int:
        """Calculate the balance factor of a node for AVL balancing."""
        return self.__get_height(node.left) - self.__get_height(node.right) if node else 0

    def __get_by_index(self, index: int) -> Optional[Player]:
        """
        Get the player at a specific index in sorted order.
        Time Complexity: O(log n) for balanced tree.
        :param index: The index of the player to retrieve (0-based).
        :return: The Player at the specified index, or None if index is out of bounds.
        """

        def helper(node: Optional[_TreeNode], idx: int) -> Optional[Player]:
            if not node:
                return None

            left_size: int = self.__get_size(node.left)

            if idx < left_size:
                return helper(node.left, idx)
            elif idx == left_size:
                return node.player
            else:
                return helper(node.right, idx - left_size - 1)

        return helper(self.__root, index)

    def __update_node(self, node: Optional[_TreeNode]) -> None:
        """Update height and size of a node based on its children."""
        if node:
            node.height = 1 + max(self.__get_height(node.left), self.__get_height(node.right))
            node.size = 1 + self.__get_size(node.left) + self.__get_size(node.right)

    def __left_rotate(self, root: _TreeNode) -> _TreeNode:
        """
        Perform a left rotation on the given root node and return the new root.
        Time Complexity: O(1)
        :param root: The node to rotate around (the subtree root that is unbalanced).
        :return: The new root of the subtree after rotation.
        """
        new_root: _TreeNode = root.right
        root.right = new_root.left
        new_root.left = root
        self.__update_node(root)
        self.__update_node(new_root)
        return new_root

    def __right_rotate(self, root: _TreeNode) -> _TreeNode:
        """
        Perform a right rotation on the given root node and return the new root.
        Time Complexity: O(1)
        :param root: The node to rotate around (the subtree root that is unbalanced).
        :return: The new root of the subtree after rotation.
        """
        new_root: _TreeNode = root.left
        root.left = new_root.right
        new_root.right = root
        self.__update_node(root)
        self.__update_node(new_root)
        return new_root

    def __insert(self, root: Optional[_TreeNode], value: Player) -> _TreeNode:
        """
        Insert a player into the AVL tree and return the new root of the subtree.
        Time Complexity: O(log n)
        :param root: The current root of the subtree where the value should be inserted.
        :param value: The Player to insert.
        :return: The new root of the subtree after insertion and balancing.
        """
        if not root:
            return _TreeNode(value)
        elif value < root.player:
            root.left = self.__insert(root.left, value)
        elif value > root.player:
            root.right = self.__insert(root.right, value)
        else:
            return root

        self.__update_node(root)
        balance = self.__get_balance(root)

        if balance > 1 and value < root.left.player:
            return self.__right_rotate(root)

        if balance < -1 and value > root.right.player:
            return self.__left_rotate(root)

        if balance > 1 and value > root.left.player:
            root.left = self.__left_rotate(root.left)
            return self.__right_rotate(root)

        if balance < -1 and value < root.right.player:
            root.right = self.__right_rotate(root.right)
            return self.__left_rotate(root)

        return root

    def __delete(self, root: Optional[_TreeNode], value: Player) -> Optional[_TreeNode]:
        """
        Delete a player from the AVL tree and return the new root of the subtree.
        Time Complexity: O(log n)
        :param root: The current root of the subtree where the value should be deleted.
        :param value: The Player to delete.
        :return: The new root of the subtree after deletion and balancing.
        """
        if not root:
            return root

        if value < root.player:
            root.left = self.__delete(root.left, value)
        elif value > root.player:
            root.right = self.__delete(root.right, value)
        else:
            if not root.left:
                return root.right
            elif not root.right:
                return root.left

            temp = self.__get_min_value_node(root.right)
            root.player = temp.player
            root.right = self.__delete(root.right, temp.player)

        if not root:
            return root

        self.__update_node(root)
        balance: int = self.__get_balance(root)

        if balance > 1 and self.__get_balance(root.left) >= 0:
            return self.__right_rotate(root)

        if balance < -1 and self.__get_balance(root.right) <= 0:
            return self.__left_rotate(root)

        if balance > 1 and self.__get_balance(root.left) < 0:
            root.left = self.__left_rotate(root.left)
            return self.__right_rotate(root)

        if balance < -1 and self.__get_balance(root.right) > 0:
            root.right = self.__right_rotate(root.right)
            return self.__left_rotate(root)

        return root

    def __len__(self) -> int:
        """Return the number of elements in the tree"""
        return self.__get_size(self.__root)

    def __getitem__(self, key: int | slice) -> Player | list[Player]:
        """
        Get player(s) by index or slice.
        Time Complexity: O(log n) for single index, O(k log n) for slice of k elements in balanced tree.
        :param key: An integer index or a slice object to retrieve player(s) from the tree.
        :return: The Player at the specified index, or a list of Players for a slice.
        """
        if isinstance(key, slice):
            start, stop, step = key.indices(len(self))
            return [self.__get_by_index(i) for i in range(start, stop, step)]
        elif isinstance(key, int):
            if key < 0:
                key += len(self)
            if key < 0 or key >= len(self):
                raise IndexError("AVLTree index out of range")
            return self.__get_by_index(key)
        else:
            raise TypeError(f"indices must be integers or slices, not {type(key).__name__}")

    def __iter__(self) -> Iterator[Player]:
        """
        In-order traversal of the tree to yield players in sorted order.
        Time Complexity: O(n)
        :return: An iterator over the players in sorted order.
        """

        def inorder(node: Optional[_TreeNode]) -> Iterator[Player]:
            if node:
                yield from inorder(node.left)
                yield node.player
                yield from inorder(node.right)

        return inorder(self.__root)

    def __contains__(self, value: Player) -> bool:
        """
        Check if a player is in the tree.
        Time Complexity: O(log n)
        :param value: The Player to check for existence in the tree.
        :return: True if the player is in the tree, False otherwise.
        """

        def search(node: Optional[_TreeNode], val: Player) -> bool:
            if not node:
                return False
            if val == node.player:
                return True
            elif val < node.player:
                return search(node.left, val)
            else:
                return search(node.right, val)

        return search(self.__root, value)

    def __repr__(self) -> str:
        """String representation of the tree"""
        return f"SortedSet({list(self)})"

    def index(self, value: Player) -> int:
        """
        Get the index of a player in sorted order.
        Time Complexity: O(log n)
        :param value: The Player to find the index of.
        :return: The index of the player in sorted order.
        """

        def helper(node: Optional[_TreeNode], accumulated_index: int) -> int:
            if not node:
                return -1

            if value < node.player:
                return helper(node.left, accumulated_index)
            elif value > node.player:
                left_and_current = self.__get_size(node.left) + 1
                return helper(node.right, accumulated_index + left_and_current)
            else:
                return accumulated_index + self.__get_size(node.left)

        result = helper(self.__root, 0)
        if result == -1:
            raise ValueError(f"{value} is not in SortedSet")
        return result

    def add(self, value: Player) -> None:
        """
        Add a player to the tree.
        Time Complexity: O(log n)
        :param value: The Player to add to the tree.
        """
        self.__root = self.__insert(self.__root, value)

    def remove(self, value: Player) -> None:
        """
        Remove a player from the tree.
        Time Complexity: O(log n)
        :param value: The Player to remove from the tree.
        """
        if value not in self:
            raise ValueError(f"{value} is not in SortedSet")
        self.__root = self.__delete(self.__root, value)
