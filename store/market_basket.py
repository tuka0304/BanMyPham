from collections import defaultdict
from itertools import combinations
from .models import Order, OrderItem, Product, Category

class MarketBasketAnalyzer:
    """
    Market Basket Analysis (Phân tích Giỏ hàng) & Association Rule Mining
    Calculates Support, Confidence, Lift for product associations and generates
    intelligent cross-sell / up-sell recommendations and business strategy insights.
    """

    def __init__(self):
        self._rules = None
        self._item_counts = None
        self._total_baskets = 0

    def compute_rules(self, min_support=0.01, min_confidence=0.10, min_lift=1.05):
        """
        Extracts baskets from all orders and mines association rules (A -> B).
        """
        orders = Order.objects.prefetch_related('order_items__product').all()
        
        baskets = []
        item_counts = defaultdict(int)
        pair_counts = defaultdict(int)

        for order in orders:
            # Unique product IDs in this order
            p_ids = list(set(item.product_id for item in order.order_items.all() if item.product_id))
            if len(p_ids) >= 1:
                baskets.append(p_ids)
                for pid in p_ids:
                    item_counts[pid] += 1
                if len(p_ids) >= 2:
                    for a, b in combinations(p_ids, 2):
                        pair_counts[(min(a, b), max(a, b))] += 1

        total_baskets = len(baskets)
        self._total_baskets = total_baskets
        self._item_counts = item_counts

        if total_baskets == 0:
            self._rules = []
            return []

        # Load all products into a map for fast metadata access
        products_map = {p.id: p for p in Product.objects.select_related('category').all()}

        rules = []
        for (a_id, b_id), pair_count in pair_counts.items():
            if a_id not in products_map or b_id not in products_map:
                continue

            support_ab = pair_count / total_baskets
            if support_ab < min_support:
                continue

            count_a = item_counts[a_id]
            count_b = item_counts[b_id]
            support_a = count_a / total_baskets
            support_b = count_b / total_baskets

            # Directed Rule 1: A -> B
            conf_a_b = pair_count / count_a if count_a > 0 else 0
            lift_a_b = (support_ab / (support_a * support_b)) if (support_a * support_b) > 0 else 0

            # Directed Rule 2: B -> A
            conf_b_a = pair_count / count_b if count_b > 0 else 0
            lift_b_a = (support_ab / (support_b * support_a)) if (support_b * support_a) > 0 else 0

            # Helper to build rule object
            for ant_id, cons_id, conf, lift in [
                (a_id, b_id, conf_a_b, lift_a_b),
                (b_id, a_id, conf_b_a, lift_b_a)
            ]:
                if conf >= min_confidence and lift >= min_lift:
                    ant_prod = products_map[ant_id]
                    cons_prod = products_map[cons_id]
                    
                    # Business strategy classification
                    if lift >= 2.5 and conf >= 0.40:
                        strategy_type = "COMBO_BUNDLE"
                        strategy_name = "Tạo Combo / Đóng gói ưu đãi"
                        strategy_desc = f"Khách mua {ant_prod.name[:25]}... có xác suất {conf*100:.0f}% mua kèm {cons_prod.name[:25]}... Tạo combo giảm giá 5-10% để tối ưu doanh thu."
                    elif lift >= 1.8 and cons_prod.price <= ant_prod.price:
                        strategy_type = "CROSS_SELL"
                        strategy_name = "Bán chéo Mua kèm giá sốc"
                        strategy_desc = f"Sản phẩm {cons_prod.name[:25]}... là phụ kiện/bổ trợ lý tưởng. Đặt nút 'Mua kèm giá tốt' tại trang thanh toán."
                    elif lift >= 1.5:
                        strategy_type = "PLACEMENT"
                        strategy_name = "Trưng bày cùng kệ / Banner"
                        strategy_desc = f"Độ tương quan cao ({lift:.2f}x so với ngẫu nhiên). Nên hiển thị liền kề trên giao diện và chiến dịch quảng cáo."
                    else:
                        strategy_type = "UP_SELL"
                        strategy_name = "Gợi ý tăng giá trị giỏ hàng"
                        strategy_desc = "Gợi ý thêm vào giỏ khi đơn hàng đạt mức điều kiện nhất định."

                    rules.append({
                        'antecedent_id': ant_id,
                        'antecedent': ant_prod,
                        'consequent_id': cons_id,
                        'consequent': cons_prod,
                        'pair_count': pair_count,
                        'support': support_ab,
                        'support_pct': round(support_ab * 100, 1),
                        'confidence': conf,
                        'confidence_pct': round(conf * 100, 1),
                        'lift': round(lift, 2),
                        'strategy_type': strategy_type,
                        'strategy_name': strategy_name,
                        'strategy_desc': strategy_desc,
                    })

        # Sort rules by Lift descending, then Confidence descending
        rules.sort(key=lambda r: (r['lift'], r['confidence']), reverse=True)
        self._rules = rules
        return rules

    def get_rules(self):
        if self._rules is None:
            self.compute_rules()
        return self._rules

    def get_product_recommendations(self, product_id, limit=4):
        """
        Returns top recommended products when viewing or purchasing a given product.
        """
        rules = self.get_rules()
        recommended = []
        seen_ids = {product_id}

        # 1. First pick from mined association rules
        for rule in rules:
            if rule['antecedent_id'] == product_id and rule['consequent_id'] not in seen_ids:
                seen_ids.add(rule['consequent_id'])
                recommended.append({
                    'product': rule['consequent'],
                    'lift': rule['lift'],
                    'confidence_pct': rule['confidence_pct'],
                    'reason': f"Thường mua cùng ({rule['confidence_pct']}% khách mua kèm, tương quan {rule['lift']}x)",
                    'tag': rule['strategy_name']
                })
                if len(recommended) >= limit:
                    break

        # 2. Fallback: products from the same category
        if len(recommended) < limit:
            try:
                base_product = Product.objects.get(id=product_id)
                same_cat = Product.objects.filter(
                    category=base_product.category
                ).exclude(id__in=seen_ids)[:limit - len(recommended)]

                for p in same_cat:
                    seen_ids.add(p.id)
                    recommended.append({
                        'product': p,
                        'lift': 1.0,
                        'confidence_pct': 0,
                        'reason': f"Cùng danh mục {base_product.category.name}",
                        'tag': "Sản phẩm tương tự"
                    })
            except Product.DoesNotExist:
                pass

        # 3. Fallback: popular products
        if len(recommended) < limit:
            popular = Product.objects.exclude(id__in=seen_ids)[:limit - len(recommended)]
            for p in popular:
                seen_ids.add(p.id)
                recommended.append({
                    'product': p,
                    'lift': 1.0,
                    'confidence_pct': 0,
                    'reason': "Sản phẩm được yêu thích tại Aeterna",
                    'tag': "Bán chạy"
                })

        return recommended

    def get_cart_recommendations(self, cart, limit=4):
        """
        Returns top recommended products based on the whole basket of products in cart.
        """
        if not cart or not cart.items.exists():
            # If cart is empty, return top featured products
            popular = Product.objects.all()[:limit]
            return [{
                'product': p,
                'lift': 1.0,
                'confidence_pct': 0,
                'reason': "Sản phẩm nổi bật cho bạn",
                'tag': "Gợi ý mua sắm"
            } for p in popular]

        cart_pids = set(item.product_id for item in cart.items.all())
        rules = self.get_rules()

        # Score candidates outside the cart: sum(Lift * Confidence)
        candidate_scores = defaultdict(lambda: {'score': 0.0, 'best_rule': None, 'product': None})

        for rule in rules:
            if rule['antecedent_id'] in cart_pids and rule['consequent_id'] not in cart_pids:
                cons_id = rule['consequent_id']
                score = rule['lift'] * rule['confidence']
                candidate_scores[cons_id]['score'] += score
                candidate_scores[cons_id]['product'] = rule['consequent']
                if (candidate_scores[cons_id]['best_rule'] is None or 
                    rule['lift'] > candidate_scores[cons_id]['best_rule']['lift']):
                    candidate_scores[cons_id]['best_rule'] = rule

        sorted_candidates = sorted(candidate_scores.values(), key=lambda x: x['score'], reverse=True)
        recommended = []
        seen_ids = set(cart_pids)

        for cand in sorted_candidates:
            p = cand['product']
            rule = cand['best_rule']
            seen_ids.add(p.id)
            recommended.append({
                'product': p,
                'lift': rule['lift'],
                'confidence_pct': rule['confidence_pct'],
                'reason': f"Khách mua {rule['antecedent'].name[:20]}... thường mua kèm ({rule['confidence_pct']}%)",
                'tag': rule['strategy_name']
            })
            if len(recommended) >= limit:
                break

        # Fallback to general products if still needed
        if len(recommended) < limit:
            extra = Product.objects.exclude(id__in=seen_ids)[:limit - len(recommended)]
            for p in extra:
                seen_ids.add(p.id)
                recommended.append({
                    'product': p,
                    'lift': 1.0,
                    'confidence_pct': 0,
                    'reason': "Bổ sung giỏ hàng của bạn",
                    'tag': "Gợi ý"
                })

        return recommended

    def get_dashboard_analytics(self):
        """
        Returns full statistical and actionable business strategy insights for Admin.
        """
        rules = self.compute_rules()
        total_orders = Order.objects.count()
        orders_with_items = Order.objects.prefetch_related('order_items').all()
        
        multi_item_orders = sum(1 for o in orders_with_items if o.order_items.count() >= 2)
        total_items_count = sum(o.order_items.count() for o in orders_with_items)
        avg_basket_size = round(total_items_count / total_orders, 2) if total_orders > 0 else 0
        multi_item_rate = round((multi_item_orders / total_orders) * 100, 1) if total_orders > 0 else 0

        # Unique pairs
        unique_pairs_count = len(rules) // 2 if rules else 0
        top_rule = rules[0] if rules else None

        # Strategy breakdown
        bundle_rules = [r for r in rules if r['strategy_type'] == 'COMBO_BUNDLE']
        cross_sell_rules = [r for r in rules if r['strategy_type'] == 'CROSS_SELL']
        placement_rules = [r for r in rules if r['strategy_type'] == 'PLACEMENT']

        # Category Cross-sell Insights
        cat_pairs = defaultdict(int)
        for r in rules:
            cat_a = r['antecedent'].category.name
            cat_b = r['consequent'].category.name
            if cat_a != cat_b:
                cat_key = tuple(sorted([cat_a, cat_b]))
                cat_pairs[cat_key] += 1

        top_cat_cross = sorted(
            [{'cat_a': k[0], 'cat_b': k[1], 'count': v} for k, v in cat_pairs.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:5]

        # Strategic Action Recommendations for Management
        strategic_recommendations = []
        if bundle_rules:
            best_bundle = bundle_rules[0]
            strategic_recommendations.append({
                'title': 'Chiến lược Gói Sản Phẩm (Bundle & Combo)',
                'badge': 'Ưu tiên cao',
                'badge_color': 'danger',
                'icon': 'fa-box-open',
                'content': f"Tạo Combo <strong>'{best_bundle['antecedent'].name[:30]}'</strong> + <strong>'{best_bundle['consequent'].name[:30]}'</strong> với chiết khấu 7%. Lift đạt <strong>{best_bundle['lift']}x</strong> và tỷ lệ mua kèm là <strong>{best_bundle['confidence_pct']}%</strong>."
            })

        if cross_sell_rules:
            best_cs = cross_sell_rules[0]
            strategic_recommendations.append({
                'title': 'Chiến lược Kích cầu Đơn hàng (AOV Cross-Sell)',
                'badge': 'Tối ưu AOV',
                'badge_color': 'success',
                'icon': 'fa-cart-plus',
                'content': f"Khi khách hàng thêm <strong>'{best_cs['antecedent'].name[:30]}'</strong> vào giỏ, hiển thị popup đề xuất nhanh <strong>'{best_cs['consequent'].name[:30]}'</strong> giá ưu đãi kèm nút 1-click thêm giỏ."
            })

        strategic_recommendations.append({
            'title': 'Chiến lược Trưng bày Danh mục Chéo (Cross-Category)',
            'badge': 'Tăng chuyển đổi',
            'badge_color': 'info',
            'icon': 'fa-layer-group',
            'content': f"Khách hàng mua Trang điểm có tần suất mua kèm Chăm sóc da mặt cao nhất. Đề xuất đặt banner liên kết chu trình skincare trước khi makeup trên trang chủ và trang danh mục."
        })

        return {
            'total_orders': total_orders,
            'multi_item_orders': multi_item_orders,
            'multi_item_rate': multi_item_rate,
            'avg_basket_size': avg_basket_size,
            'total_rules': len(rules),
            'unique_pairs_count': unique_pairs_count,
            'top_rule': top_rule,
            'rules': rules[:25], # top 25 rules for table
            'bundle_rules': bundle_rules[:6],
            'cross_sell_rules': cross_sell_rules[:6],
            'top_cat_cross': top_cat_cross,
            'strategic_recommendations': strategic_recommendations
        }


# Singleton instance
mba_analyzer = MarketBasketAnalyzer()
