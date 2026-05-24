from search.widgets import WidgetFactory, SearchContext


def test_analyze_logs_widget_activation():
    results = [
        {"path": "C:/logs/error1.log", "extension": ".log", "file_type": "text", "preview": "ERROR failed to start"},
        {"path": "C:/logs/error2.log", "extension": ".log", "file_type": "text", "preview": "WARNING disk space low"},
        {"path": "C:/logs/other.log", "extension": ".log", "file_type": "text", "preview": "Traceback (most recent call last)"},
    ]
    context = SearchContext(query="show logs", parsed={}, results=results)
    active = WidgetFactory().get_active_widgets(context)
    assert any(widget.name == "Analyze Logs" for widget in active)


def test_view_gallery_widget_activation():
    results = [
        {"path": "C:/images/photo1.jpg", "extension": ".jpg", "file_type": "image", "preview": "[Image] dominant color: blue"},
        {"path": "C:/images/photo2.png", "extension": ".png", "file_type": "image", "preview": "[Image] dominant color: green"},
        {"path": "C:/images/photo3.gif", "extension": ".gif", "file_type": "image", "preview": "[Image] dominant color: pink"},
        {"path": "C:/images/photo4.jpeg", "extension": ".jpeg", "file_type": "image", "preview": "[Image] dominant color: orange"},
        {"path": "C:/images/photo5.bmp", "extension": ".bmp", "file_type": "image", "preview": "[Image] dominant color: red"},
    ]
    context = SearchContext(query="image gallery", parsed={}, results=results)
    active = WidgetFactory().get_active_widgets(context)
    assert any(widget.name == "View as Gallery" for widget in active)


def test_no_widget_activation_for_generic_text_results():
    results = [
        {"path": "C:/docs/readme.txt", "extension": ".txt", "file_type": "text", "preview": "This is a simple document."},
        {"path": "C:/docs/notes.md", "extension": ".md", "file_type": "text", "preview": "Some markdown notes."},
    ]
    context = SearchContext(query="search documents", parsed={}, results=results)
    active = WidgetFactory().get_active_widgets(context)
    assert active == []
