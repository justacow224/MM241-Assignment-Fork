from policy import Policy
import numpy as np
import random

class Policy2053589_2252792_2211720_2211078_2352687(Policy):
    def __init__(self, policy_id=2, stocks=None, products=None):
        assert policy_id in [1, 2], "Policy ID must be 1 or 2"
        self.policy_id = policy_id

    def _get_state_key(self, observation, info):
        return str(observation)

    def get_action(self, observation, info):
        if self.policy_id == 1:
            # Use the heuristic-based algorithm
            action = self.GreedyPolicyHeuristic(observation, info)
        else:
            # Use the BFS-based algorithm
            action = self.GreedyPolicyBFS(observation, info)
        return action

    def GreedyPolicyHeuristic(self, observation, info):
        # Sort products by priority or size (default heuristic: largest first)
        list_prods = sorted(
            observation["products"],
            key=lambda p: (p.get("priority", 0), max(p["size"])),  # Higher priority and larger size first
            reverse=True,
        )

        def heuristic_fit():
            for prod in list_prods:
                if prod["quantity"] > 0:
                    prod_size = prod["size"]
                    best_score = float("inf")
                    best_placement = None

                    for i, stock in enumerate(observation["stocks"]):
                        stock_w, stock_h = self._get_stock_size_(stock)

                        # Skip stocks smaller than the product
                        if stock_w < prod_size[0] or stock_h < prod_size[1]:
                            continue

                        # Check original orientation
                        placement = self._find_best_position(stock, prod_size, stock_w, stock_h)
                        if placement:
                            score = self._calculate_heuristic(stock, prod_size, placement, stock_w, stock_h)
                            if score < best_score:
                                best_score = score
                                best_placement = {"stock_idx": i, "size": prod_size, "position": placement}

                        # Check rotated orientation
                        if prod_size[0] != prod_size[1]:  # If not square
                            rotated_size = prod_size[::-1]
                            if stock_w >= rotated_size[0] and stock_h >= rotated_size[1]:
                                placement = self._find_best_position(stock, rotated_size, stock_w, stock_h)
                                if placement:
                                    score = self._calculate_heuristic(stock, rotated_size, placement, stock_w, stock_h)
                                    if score < best_score:
                                        best_score = {
                                            "stock_idx": i,
                                            "size": rotated_size,
                                            "position": placement,
                                        }

                    if best_placement:
                        return best_placement

            # No valid placement found
            return {"stock_idx": -1, "size": [0, 0], "position": (0, 0)}

        return heuristic_fit()

    def GreedyPolicyBFS(self, observation, info):
        list_prods = observation["products"]

        def bfs():
            for prod in list_prods:
                if prod["quantity"] > 0:
                    prod_size = prod["size"]
                    stack = []

                    # Initialize stack with all stocks
                    for i, stock in enumerate(observation["stocks"]):
                        stock_w, stock_h = self._get_stock_size_(stock)
                        stack.append((i, stock, stock_w, stock_h, prod_size, (None, None)))

                    while stack:
                        stock_idx, stock, stock_w, stock_h, current_prod_size, position = stack.pop()

                        # Check for valid placement in current orientation
                        for x in range(stock_w - current_prod_size[0] + 1):
                            for y in range(stock_h - current_prod_size[1] + 1):
                                if self._can_place_(stock, (x, y), current_prod_size):
                                    return {"stock_idx": stock_idx, "size": current_prod_size, "position": (x, y)}

                        # Try rotated orientation
                        if current_prod_size[0] != current_prod_size[1]:
                            rotated_size = current_prod_size[::-1]
                            for x in range(stock_w - rotated_size[0] + 1):
                                for y in range(stock_h - rotated_size[1] + 1):
                                    if self._can_place_(stock, (x, y), rotated_size):
                                        return {"stock_idx": stock_idx, "size": rotated_size, "position": (x, y)}

            # No valid placement found
            return {"stock_idx": -1, "size": [0, 0], "position": (0, 0)}

        return bfs()

    def _find_best_position(self, stock, prod_size, stock_w, stock_h):
        """
        Find the best position for the product based on heuristic scoring.
        """
        best_position = None
        for x in range(stock_w - prod_size[0] + 1):
            for y in range(stock_h - prod_size[1] + 1):
                if self._can_place_(stock, (x, y), prod_size):
                    best_position = (x, y)
                    break  # Early exit on first valid position
            if best_position:
                break
        return best_position

    def _calculate_heuristic(self, stock, prod_size, position, stock_w, stock_h):
        """
        Calculate a heuristic score for placing the product at the given position.
        Lower scores indicate better placements.
        """
        x, y = position
        used_space = prod_size[0] * prod_size[1]
        total_space = stock_w * stock_h

        # Heuristic: prioritize minimizing wasted space and placing closer to (0,0)
        wasted_space = total_space - used_space
        proximity_penalty = x + y  # Closer to (0,0) is better
        free_space_score = (stock_w - prod_size[0]) * (stock_h - prod_size[1])

        # Weighted sum for heuristic score
        return wasted_space + proximity_penalty - free_space_score


