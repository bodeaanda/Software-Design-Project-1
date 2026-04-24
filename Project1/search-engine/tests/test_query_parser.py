from search.query_parser import QueryParser

def test_path_qualifier():
    parser = QueryParser()
    result = parser.parse("path:Arduino")
    assert result["path"] == ["Arduino"]
    assert result["content"] == []

def test_content_qualifier():
    parser = QueryParser()
    result = parser.parse("content:ESP32")
    assert result["content"] == ["ESP32"]
    assert result["path"] == []

def test_combined_qualifiers():
    parser = QueryParser()
    result = parser.parse("path:Arduino content:ESP32")
    assert result["path"] == ["Arduino"]
    assert result["content"] == ["ESP32"]

def test_general_term():
    parser = QueryParser()
    result = parser.parse("Arduino")
    assert result["general"] == ["Arduino"]

def test_multiple_path_terms():
    parser = QueryParser()
    result = parser.parse("path:Arduino path:lab1")
    assert result["path"] == ["Arduino", "lab1"]