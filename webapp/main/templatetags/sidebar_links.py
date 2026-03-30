from django import template

register = template.Library();

@register.simple_tag
def get_links():
    return [{
        'name': 'Home',
        'href': '/',
        'icon': 'fa-house',
    }, {
        'name': 'Cars',
        'href': '/cars',
        'icon': 'fa-car',
    }, {
        'name': 'Contact',
        'href': '/contact',
        'icon': 'fa-paper-plane',
    }, {
        'name': 'About',
        'href': '/about',
        'icon': 'fa-address-card',
    },{
        'name': 'Katalog',
        'href': '/katalog/',
        'icon': 'fa-book-open',
    },{
        'name': 'Add to katalog',
        'href': '/katalog/new-post/',
        'icon': 'fa-plus',
    },{
        'name': 'Społeczność',
        'href': '/spolecznosc/',
        'icon': 'fa-comment', #look for your icon here https://fontawesome.com/search?ic=free
    }]
    
