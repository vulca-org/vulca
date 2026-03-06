"""Graph node wrappers for existing Agents.

Each node adapts an existing Agent class to the LangGraph node interface:
    (PipelineState) -> dict   # returns partial state update

Importing this package triggers all @AgentRegistry.register decorators.
"""

from app.prototype.graph.nodes.scout_node import ScoutNode         # noqa: F401
from app.prototype.graph.nodes.router_node import RouterNode       # noqa: F401
from app.prototype.graph.nodes.draft_node import DraftNode         # noqa: F401
from app.prototype.graph.nodes.critic_node import CriticNode       # noqa: F401
from app.prototype.graph.nodes.queen_node import QueenNode         # noqa: F401
from app.prototype.graph.nodes.archivist_node import ArchivistNode # noqa: F401
from app.prototype.graph.nodes.report_node import ReportNode       # noqa: F401
