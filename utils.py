#!/usr/bin/env python3
"""
Utility functions for Scira.ai API

This module provides utility functions for parsing and handling responses from the Scira.ai API.
"""

import json
import re
from typing import Dict, List, Any, Iterator, Optional, Union, Tuple


def parse_stream_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse a line from the streaming response.
    
    Args:
        line: A line from the streaming response
        
    Returns:
        Parsed data or None if the line couldn't be parsed
    """
    if not line or not line.strip():
        return None
    
    # Lines typically start with a prefix like "f:", "9:", "8:", "a:", etc.
    prefix_match = re.match(r'^([a-zA-Z0-9]+):(.*)$', line)
    if not prefix_match:
        return {"type": "unknown", "text": line}
    
    prefix, content = prefix_match.groups()
    
    try:
        # Try to parse as JSON
        data = json.loads(content)
        return {"type": "json", "prefix": prefix, "data": data}
    except json.JSONDecodeError:
        # Not valid JSON, return as text
        return {"type": "text", "prefix": prefix, "text": content}


def process_stream(response_iter: Iterator[bytes]) -> Iterator[Dict[str, Any]]:
    """Process a streaming response from the Scira.ai API.
    
    Args:
        response_iter: Iterator of response chunks
        
    Yields:
        Parsed chunks of the response
    """
    buffer = ""
    
    for chunk in response_iter:
        if not chunk:
            continue
            
        # Convert bytes to string if needed
        if isinstance(chunk, bytes):
            chunk = chunk.decode('utf-8')
            
        buffer += chunk
        
        # Process each line in the buffer
        while '\n' in buffer:
            line, buffer = buffer.split('\n', 1)
            
            parsed = parse_stream_line(line)
            if parsed:
                yield parsed


def extract_search_results(stream_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract search results from stream data.
    
    Args:
        stream_data: List of parsed stream data
        
    Returns:
        List of search results
    """
    results = []
    
    for item in stream_data:
        if item.get("type") != "json":
            continue
            
        data = item.get("data", {})
        
        # Handle search results
        if "result" in data and "searches" in data["result"]:
            for search in data["result"]["searches"]:
                if "results" in search:
                    results.extend(search["results"])
    
    return results


def extract_search_queries(stream_data: List[Dict[str, Any]]) -> List[str]:
    """Extract search queries from stream data.
    
    Args:
        stream_data: List of parsed stream data
        
    Returns:
        List of search queries
    """
    queries = []
    
    for item in stream_data:
        if item.get("type") != "json":
            continue
            
        data = item.get("data", {})
        
        # Handle tool calls with web_search
        if "toolName" in data and data["toolName"] == "web_search" and "args" in data:
            if "queries" in data["args"]:
                queries.extend(data["args"]["queries"])
        
        # Handle query completion data
        if isinstance(data, list) and data and "type" in data[0]:
            if data[0]["type"] == "query_completion" and "data" in data[0]:
                query = data[0]["data"].get("query")
                if query:
                    queries.append(query)
    
    return queries


def format_search_result(result: Dict[str, Any], include_content: bool = True) -> str:
    """Format a single search result for display.
    
    Args:
        result: Search result dictionary
        include_content: Whether to include the content
        
    Returns:
        Formatted string
    """
    lines = []
    
    title = result.get("title", "No Title")
    url = result.get("url", "No URL")
    
    lines.append(f"Title: {title}")
    lines.append(f"URL: {url}")
    
    if include_content:
        content = result.get("content", "").strip()
        if content:
            # Truncate content if it's too long
            if len(content) > 300:
                content = content[:297] + "..."
            lines.append(f"Content: {content}")
    
    return "\n".join(lines)


def format_search_results(results: List[Dict[str, Any]], include_content: bool = True) -> str:
    """Format search results for display.
    
    Args:
        results: List of search result dictionaries
        include_content: Whether to include the content
        
    Returns:
        Formatted string of search results
    """
    if not results:
        return "No search results found."
    
    formatted = []
    
    for i, result in enumerate(results, 1):
        formatted.append(f"\n[{i}] {format_search_result(result, include_content)}")
    
    return "\n".join(formatted)


def extract_message_id(stream_data: List[Dict[str, Any]]) -> Optional[str]:
    """Extract message ID from stream data.
    
    Args:
        stream_data: List of parsed stream data
        
    Returns:
        Message ID or None if not found
    """
    for item in stream_data:
        if item.get("type") != "json":
            continue
            
        data = item.get("data", {})
        
        if "messageId" in data:
            return data["messageId"]
    
    return None


def generate_random_id(length: int = 10) -> str:
    """Generate a random ID string.
    
    Args:
        length: Length of the random ID
        
    Returns:
        A random string ID
    """
    import uuid
    return str(uuid.uuid4()).replace("-", "")[:length]
