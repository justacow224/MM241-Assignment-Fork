from policy import Policy

class Policy2213332(Policy):
    def __init__(self, policy_id=1):
        assert policy_id in [1, 2], "Policy ID must be 1 or 2"
        self.policy_id = policy_id

    def get_action(self, observation, info):
        if self.policy_id == 1:
            return self.near_optimal_cutting_action(observation)
        elif self.policy_id == 2:
            return self.two_dimensional_cutting_action(observation)

    def near_optimal_cutting_action(self, observation):
        list_prods = observation["products"]  # Danh sách các sản phẩm cần cắt
        stock_idx = -1  # Chỉ số cuộn được chọn
        pos_x, pos_y = None, None  # Vị trí cắt tạm thời

        # Lọc các sản phẩm có số lượng > 0 và sắp xếp theo diện tích (từ lớn đến nhỏ)
        prod_sizes = sorted(
            [prod["size"] for prod in list_prods if prod["quantity"] > 0],
            key=lambda x: x[0] * x[1],  # Tính diện tích sản phẩm
            reverse=True,  # Sắp xếp theo diện tích lớn đến nhỏ
        )
        
        if not prod_sizes:
            return {"stock_idx": -1, "size": [0, 0], "position": (0, 0)}

        def fit_item_in_stock(stock, item):
            stock_w, stock_h = self._get_stock_size_(stock)  # Lấy kích thước cuộn
            positions = []  # Danh sách các vị trí có thể cắt sản phẩm

            # Kiểm tra các vị trí không xoay sản phẩm
            for x in range(stock_w - item[0] + 1):
                for y in range(stock_h - item[1] + 1):
                    if self._can_place_(stock, (x, y), item):  # Kiểm tra xem sản phẩm có thể đặt tại vị trí này không
                        positions.append((x, y, item))  # Lưu vị trí hợp lệ

            # Kiểm tra các vị trí với sản phẩm xoay 90 độ
            rotated_item = (item[1], item[0])  # Đảo chiều dài và chiều rộng của sản phẩm
            for x in range(stock_w - rotated_item[0] + 1):
                for y in range(stock_h - rotated_item[1] + 1):
                    if self._can_place_(stock, (x, y), rotated_item):  # Kiểm tra xem sản phẩm xoay có thể đặt tại vị trí này không
                        positions.append((x, y, rotated_item))  # Lưu vị trí hợp lệ

            # Chọn vị trí có diện tích dư thừa ít nhất
            best_position = None
            min_residual = float("inf")  # Khởi tạo diện tích dư thừa tối thiểu
            for pos in positions:
                residual_space = (
                    (stock_w - (pos[0] + pos[2][0])) * stock_h +
                    (stock_h - (pos[1] + pos[2][1])) * stock_w
                )  # Tính diện tích dư thừa
                if residual_space < min_residual:  # Nếu diện tích dư thừa ít hơn, chọn vị trí này
                    min_residual = residual_space
                    best_position = pos

            return best_position  # Trả về vị trí tối ưu cho sản phẩm

        # Duyệt qua tất cả các cuộn và các sản phẩm để tìm vị trí cắt
        for i, stock in enumerate(observation["stocks"]):
            for item in prod_sizes:
                placement = fit_item_in_stock(stock, item)  # Tìm vị trí cắt cho sản phẩm
                if placement:
                    pos_x, pos_y, final_size = placement  # Lấy vị trí và kích thước sản phẩm sau khi cắt
                    return {"stock_idx": i, "size": final_size, "position": (pos_x, pos_y)}  # Trả về kết quả

        return {"stock_idx": -1, "size": [0, 0], "position": (0, 0)}  # Nếu không tìm được vị trí hợp lệ
    def two_dimensional_cutting_action(self, observation):
        list_prods = observation["products"]
        stock_idx, pos_x, pos_y = -1, None, None

        # Sắp xếp sản phẩm theo chiều cao giảm dần
        sorted_prods = sorted(list_prods, key=lambda x: x["size"][1], reverse=True)

        for prod in sorted_prods:
            if prod["quantity"] > 0:
                prod_size = prod["size"]
                for i, stock in enumerate(observation["stocks"]):
                    stock_w, stock_h = self._get_stock_size_(stock)

                    # Tìm vị trí cắt cho sản phẩm không xoay
                    for x in range(stock_w - prod_size[0] + 1):
                        for y in range(stock_h - prod_size[1] + 1):
                            if self._can_place_(stock, (x, y), prod_size):
                                return {"stock_idx": i, "size": prod_size, "position": (x, y)}

                    # Kiểm tra sản phẩm xoay
                    if stock_w >= prod_size[1] and stock_h >= prod_size[0]:
                        for x in range(stock_w - prod_size[1] + 1):
                            for y in range(stock_h - prod_size[0] + 1):
                                if self._can_place_(stock, (x, y), prod_size[::-1]):
                                    return {"stock_idx": i, "size": prod_size[::-1], "position": (x, y)}

        return {"stock_idx": -1, "size": [0, 0], "position": (0, 0)}  # Không tìm thấy vị trí hợp lệ
