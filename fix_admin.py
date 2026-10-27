import os

admin_dir = r"e:\cosmetics-store\templates\admin"
for f in os.listdir(admin_dir):
    if f in ['layout.html', 'index.html', 'product-list.html']:
        continue
    if not f.endswith('.html'):
        continue
    
    path = os.path.join(admin_dir, f)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Very crude conversion for other admin templates
    content = content.replace('<!DOCTYPE html>\n<html lang="en" xmlns:th="http://www.thymeleaf.org"\n      xmlns:layout="http://www.ultraq.net.nz/thymeleaf/layout"\n      layout:decorate="~{admin/layout}">\n<head>\n    <title>Cosmetics Admin Panel</title>\n</head>\n<body>\n\n<div layout:fragment="content">', '{% extends "admin/layout.html" %}\n{% block content %}')
    content = content.replace('</div>\n\n</body>\n</html>', '{% endblock %}')
    
    # Generic replaces
    content = content.replace('th:action="@{/admin/products/save}"', 'action="{% url \'admin_save_product\' %}"')
    content = content.replace('th:action="@{/admin/categories/save}"', 'action="{% url \'admin_save_category\' %}"')
    content = content.replace('th:action="@{/admin/orders/update-status}"', 'action="{% url \'admin_update_order_status\' %}"')
    content = content.replace('th:action="@{/admin/users/update-role}"', 'action="{% url \'admin_update_user_role\' %}"')
    content = content.replace('th:action="@{/admin/users/toggle-status}"', 'action="{% url \'admin_toggle_user_status\' %}"')
    content = content.replace('th:action="@{/admin/inventory/add-stock}"', 'action="{% url \'admin_add_stock\' %}"')
    
    # Simple list replacements
    content = content.replace('th:each="c : ${categories}"', '{% for c in categories %}')
    content = content.replace('th:each="order : ${orders}"', '{% for order in orders %}')
    content = content.replace('th:each="user : ${users}"', '{% for user in users %}')
    content = content.replace('th:each="p : ${products}"', '{% for p in products %}')
    
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)
