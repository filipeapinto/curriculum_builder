def chunk_list(items, size):
    """Split items into consecutive chunks of at most `size` elements."""
    chunks = []
    for i in range(0, len(items) + size, size):
        chunks.append(items[i:i + size])
    return chunks
