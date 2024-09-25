import unittest

from flowpilot.workflow.graph import NodeGraph
from flowpilot.workflow.nodes.basic import HttpReqNode, PyCodeNode

CODE_TEMPLATE = """
def hashmd5():
    import hashlib
    md5_hash = hashlib.md5()
    md5_hash.update(f"reflow_sts_{userid}_{authsk}_{timestamp}".encode("utf-8"))
    return md5_hash.hexdigest()
md5 = hashmd5()
"""


class TestPyCodeNode(unittest.TestCase):

    def test_pycode_node(self):
        node = PyCodeNode(source=CODE_TEMPLATE, output_fields=["md5"])
        node.vars.value = {
            "userid": "123456",
            "authsk": "123456",
            "timestamp": "123456",
        }
        node.execute()

    def test_http_node(self):
        node = HttpReqNode()
        node.method.value = "GET"
        node.params.value = {"url": "https://www.baidu.com"}
        node.execute()

    def test_node_connect(self):
        node1 = PyCodeNode(
            source=CODE_TEMPLATE,
            output_fields=["md5"],
        )
        node1.vars.value = {
            "userid": "123456",
            "authsk": "123456",
            "timestamp": "123456",
        }

        node2 = PyCodeNode(source="ret = md5")

        node1.then.link(node2.exec)
        node1.retv.link(node2.vars)

        graph = NodeGraph(nodes=[node1, node2])
        node1.exec.emit(graph.ctx)

        self.assertEqual(
            node2.retv.value["ret"] == "1bb311201f3826b1b0ac43f082c6b118", True
        )


if __name__ == "__main__":
    unittest.main()
