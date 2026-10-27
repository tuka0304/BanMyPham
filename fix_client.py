import os
import re

def fix_checkout():
    path = r"e:\cosmetics-store\templates\client\checkout.html"
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace('<form action="/placeOrder" method="post">', '<form action="{% url \'place_order\' %}" method="post">\n                {% csrf_token %}')
    content = content.replace('name="receiverName" value="{{ form.receiverName.value|default_if_none:\'\' }}"', 'name="receiverName"')
    content = content.replace('name="shippingAddress" value="{{ form.shippingAddress.value|default_if_none:\'\' }}"', 'name="shippingAddress"')
    content = content.replace('name="receiverPhone" value="{{ form.receiverPhone.value|default_if_none:\'\' }}"', 'name="receiverPhone"')
    
    # Actually, let's just do regex on the original file
    pass

# Read original files instead
def process_checkout():
    path = r"e:\cosmetics-store\cosmetics-store\src\main\resources\templates\client\checkout.html"
    out_path = r"e:\cosmetics-store\templates\client\checkout.html"
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    
    c = re.sub(r'<html[^>]*>', '<html>', c)
    c = c.replace('th:action="@{/placeOrder}" th:object="${order}" method="post"', 'action="{% url \'place_order\' %}" method="post">\n{% csrf_token %}')
    c = re.sub(r'th:field="\*\{([^}]+)\}"', r'name="\1"', c)
    c = c.replace('th:href="@{/cart}"', 'href="{% url \'view_cart\' %}"')
    
    # Loop
    c = re.sub(r'<tr th:each="item : \$\{cart.items\}">', '{% for item in cart.items.all %}\n<tr>', c)
    c = c.replace('</tr>\n                </tbody>', '</tr>\n{% endfor %}\n                </tbody>')
    
    # text
    c = re.sub(r'th:text="\$\{item.product.name\}"[^>]*>[^<]*</', '>{{ item.product.name }}</', c)
    c = re.sub(r'th:text="\$\{#numbers.formatDecimal\(item.product.price[^}]+\}"[^>]*>[^<]*</', '>{{ item.product.price }}đ</', c)
    c = re.sub(r'th:text="\$\{item.quantity\}"[^>]*>[^<]*</', '>{{ item.quantity }}</', c)
    c = re.sub(r'th:text="\$\{#numbers.formatDecimal\(item.product.price \* item.quantity[^}]+\}"[^>]*>[^<]*</', '>{% widthratio item.product.price 1 item.quantity %}đ</', c)
    c = re.sub(r'th:text="\$\{#numbers.formatDecimal\(totalAmount[^}]+\}"[^>]*>[^<]*</', '>{{ totalAmount }}đ</', c)
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(c)

def process_login():
    path = r"e:\cosmetics-store\cosmetics-store\src\main\resources\templates\client\login.html"
    out_path = r"e:\cosmetics-store\templates\client\login.html"
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    c = re.sub(r'<html[^>]*>', '<html>', c)
    c = c.replace('th:if="${param.registerSuccess}"', '{% if messages %}{% for msg in messages %}{% if "Đăng ký thành công" in msg.message %}')
    c = c.replace('Đăng ký thành công! Vui lòng đăng nhập.\n        </div>', 'Đăng ký thành công! Vui lòng đăng nhập.\n        </div>{% endif %}{% endfor %}{% endif %}')
    
    c = c.replace('th:if="${param.error}"', '{% if messages %}{% for msg in messages %}{% if "đúng" in msg.message or "khóa" in msg.message %}')
    c = c.replace('Tên đăng nhập hoặc mật khẩu không đúng.\n        </div>', '{{ msg.message }}\n        </div>{% endif %}{% endfor %}{% endif %}')
    
    c = c.replace('th:action="@{/perform_login}" method="post"', 'action="{% url \'login\' %}" method="post">\n{% csrf_token %}')
    c = c.replace('th:href="@{/register}"', 'href="{% url \'register\' %}"')
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(c)

def process_register():
    path = r"e:\cosmetics-store\cosmetics-store\src\main\resources\templates\client\register.html"
    out_path = r"e:\cosmetics-store\templates\client\register.html"
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    c = re.sub(r'<html[^>]*>', '<html>', c)
    c = c.replace('th:if="${registerError}"', '{% if messages %}')
    c = c.replace('<span th:text="${registerError}"></span>', '{% for msg in messages %}{{ msg }}{% endfor %}')
    c = c.replace('</div>\n        \n        <form', '{% endif %}\n        </div>\n        \n        <form')
    
    c = c.replace('th:action="@{/register}" th:object="${user}" method="post"', 'action="{% url \'register\' %}" method="post">\n{% csrf_token %}')
    c = re.sub(r'th:field="\*\{([^}]+)\}"', r'name="\1"', c)
    c = c.replace('th:href="@{/login}"', 'href="{% url \'login\' %}"')
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(c)

def process_order_list():
    path = r"e:\cosmetics-store\cosmetics-store\src\main\resources\templates\client\order-list.html"
    out_path = r"e:\cosmetics-store\templates\client\order-list.html"
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    c = re.sub(r'<html[^>]*>', '<html>', c)
    c = c.replace('th:if="${orders.isEmpty()}"', '{% if not orders %}')
    c = c.replace('th:href="@{/}"', 'href="{% url \'index\' %}"')
    c = c.replace('</a>\n        </div>', '</a>\n        </div>\n        {% endif %}')
    
    c = c.replace('<div th:each="order : ${orders}" class="order-card">', '{% for order in orders %}\n<div class="order-card">')
    
    c = re.sub(r'th:text="\$\{order.id\}"[^>]*>[^<]*</', '>{{ order.id }}</', c)
    c = re.sub(r'th:classappend="[^"]*"', '', c)
    c = re.sub(r'th:text="\$\{order.status\}"[^>]*>[^<]*</', '>{{ order.status }}</', c)
    c = re.sub(r'th:text="\$\{#temporals[^}]+\}"[^>]*>[^<]*</', '>{{ order.order_date|date:"d/M/Y H:i" }}</', c)
    c = re.sub(r'th:text="\$\{order.shippingAddress\}"[^>]*>[^<]*</', '>{{ order.shipping_address }}</', c)
    
    c = c.replace('<tr th:each="item : ${order.items}">', '{% for item in order.order_items.all %}\n<tr>')
    c = re.sub(r'th:text="\$\{item.product.name\}"[^>]*>[^<]*</', '>{{ item.product.name }}</', c)
    c = re.sub(r'th:text="\$\{item.quantity\}"[^>]*>[^<]*</', '>{{ item.quantity }}</', c)
    c = re.sub(r'th:text="\$\{#numbers.formatDecimal\(item.priceAtOrder[^}]+\}"[^>]*>[^<]*</', '>{{ item.price_at_order }}đ</', c)
    c = c.replace('</tr>\n                </tbody>', '</tr>\n{% endfor %}\n                </tbody>')
    
    c = re.sub(r'th:text="\$\{#numbers.formatDecimal\(order.totalAmount[^}]+\}"[^>]*>[^<]*</', '>{{ order.total_amount }} VND</', c)
    
    c = c.replace('<div class="back-nav">', '{% endfor %}\n<div class="back-nav">')
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(c)

process_checkout()
process_login()
process_register()
process_order_list()
