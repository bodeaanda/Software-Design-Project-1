from search.widgets import WidgetManager, SearchContext

wm = WidgetManager()

print('Triggering log search:')
wm.on_search('show logs', [
    {"path": "C:/logs/error1.log", "extension": ".log", "file_type": "text", "preview": "ERROR failed to start"},
    {"path": "C:/logs/error2.log", "extension": ".log", "file_type": "text", "preview": "WARNING disk space low"},
    {"path": "C:/logs/other.log", "extension": ".log", "file_type": "text", "preview": "Traceback (most recent call last)"},
])

print('\nTriggering image search:')
wm.on_search('image gallery', [
    {"path": "C:/images/photo1.jpg", "extension": ".jpg", "file_type": "image", "preview": "[Image] dominant color: blue"},
    {"path": "C:/images/photo2.png", "extension": ".png", "file_type": "image", "preview": "[Image] dominant color: green"},
    {"path": "C:/images/photo3.gif", "extension": ".gif", "file_type": "image", "preview": "[Image] dominant color: pink"},
    {"path": "C:/images/photo4.jpeg", "extension": ".jpeg", "file_type": "image", "preview": "[Image] dominant color: orange"},
])

print('\nTriggering generic search:')
wm.on_search('docs', [
    {"path": "C:/docs/readme.txt", "extension": ".txt", "file_type": "text", "preview": "This is a simple document."},
    {"path": "C:/docs/notes.md", "extension": ".md", "file_type": "text", "preview": "Some markdown notes."},
])
