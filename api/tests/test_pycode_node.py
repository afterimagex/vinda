import unittest

from flowpilot.workflow.graph import NodeGraph
from flowpilot.workflow.nodes.basic import PyCodeNode


class TestPyCodeNode(unittest.TestCase):

    def test_func(self):
        node1 = PyCodeNode(
            source="""
def hashmd5():
    import hashlib
    md5_hash = hashlib.md5()
    md5_hash.update(f"reflow_sts_{userid}_{authsk}_{timestamp}".encode("utf-8"))
    return md5_hash.hexdigest()
md5 = hashmd5()
""",
            output_fields=["md5"],
        )
        node1.vars.value = {
            "userid": "123456",
            "authsk": "123456",
            "timestamp": "123456",
        }

        node2 = PyCodeNode(
            source="""
ret = md5
""",
        )

        node2.vars.link(node1.retv)

        graph = NodeGraph(nodes=[node1, node2])

        print(graph)

        node1.execute()
        node2.execute()

        self.assertEqual(
            node2.retv.value["ret"] == "1bb311201f3826b1b0ac43f082c6b118", True
        )


if __name__ == "__main__":
    unittest.main()
