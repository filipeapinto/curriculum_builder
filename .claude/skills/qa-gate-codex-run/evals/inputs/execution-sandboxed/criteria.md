chunk_list(items, size) must:
1. Return every item from `items`, in order, split across chunks of at most `size`.
2. Never return an empty chunk.
3. Return an empty list when `items` is empty.
