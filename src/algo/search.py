class TrieNode:
    def __init__(self):
        self.children = {}
        self.fail = None
        self.output = []

class AhoCorasick:
    def __init__(self, keywords):
        self.root = TrieNode()
        self.build_trie(keywords)
        self.build_failure_pointers()

    def build_trie(self, keywords):
        for keyword in keywords:
            node = self.root
            for char in keyword:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
            node.output.append(keyword)

    def build_failure_pointers(self):
        from collections import deque
        queue = deque()
        for child in self.root.children.values():
            child.fail = self.root
            queue.append(child)

        while queue:
            current_node = queue.popleft()

            for char, child_node in current_node.children.items():
                queue.append(child_node)
                fail_node = current_node.fail
                while fail_node is not None and char not in fail_node.children:
                    fail_node = fail_node.fail
                child_node.fail = fail_node.children[char] if fail_node else self.root
                if child_node.fail:
                    child_node.output += child_node.fail.output

    def search(self, text):
        node = self.root
        results = {}
        for i in range(len(text)):
            char = text[i]
            while node is not None and char not in node.children:
                node = node.fail
            if node is None:
                node = self.root
                continue
            node = node.children[char]
            for pattern in node.output:
                # 紀錄模式在文本中的位置
                results[pattern] = i - len(pattern) + 1
        return results