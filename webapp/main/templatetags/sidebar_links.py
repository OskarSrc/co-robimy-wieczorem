from django import template

# Ten prosty tag zwraca linki do starszego bocznego menu.
# Lista jest wpisana ręcznie, bo ma służyć tylko do renderowania stałej nawigacji.
register = template.Library()

@register.simple_tag
def get_links():
    # To są najważniejsze skróty prowadzące do głównych sekcji projektu.
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
        'icon': 'fa-comment',  # Ikony są z darmowej paczki Font Awesome.
    }]
    
