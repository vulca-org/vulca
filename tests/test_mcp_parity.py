"""MCP CLI parity tests — ensure all 5 missing tools exist in mcp_server.py."""


class TestMCPParity:
    def test_mcp_has_sync(self):
        content = open('src/vulca/mcp_server.py').read()
        assert 'def sync_data' in content or 'async def sync_data' in content

    def test_mcp_has_layers_composite(self):
        content = open('src/vulca/mcp_server.py').read()
        assert 'def layers_composite' in content or 'def composite_layers' in content

    def test_mcp_has_layers_export(self):
        content = open('src/vulca/mcp_server.py').read()
        assert 'def layers_export' in content or 'def export_layers' in content

    def test_mcp_has_layers_evaluate(self):
        content = open('src/vulca/mcp_server.py').read()
        assert 'def layers_evaluate' in content or 'def evaluate_layers' in content

