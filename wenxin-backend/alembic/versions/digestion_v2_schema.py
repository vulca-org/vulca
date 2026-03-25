"""Digestion V2 schema — studio sessions, artifacts, signals, patterns, templates

Revision ID: digestion_v2
Revises: vulca_47d_complete
Create Date: 2026-03-25

Creates 5 tables for the Digestion V2 4-layer architecture:
- studio_sessions: Brief + state + satisfaction (Layer 0-2)
- artifacts: per-image L1-L5 structural analysis (Layer 2)
- signals: per-action user signals (Layer 1)
- evolved_patterns: cross-session learned patterns (Layer 3)
- brief_templates: auto-generated Brief templates (Layer 3)

Note: pgvector (VECTOR columns) requires `CREATE EXTENSION vector` on PostgreSQL.
On SQLite these columns are stored as TEXT (no vector search).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'digestion_v2'
down_revision: Union[str, Sequence[str], None] = 'vulca_47d_complete'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create Digestion V2 tables."""

    # ── studio_sessions ──
    op.create_table(
        'studio_sessions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('brief', sa.JSON, nullable=False),
        sa.Column('state', sa.String(20), nullable=False, server_default='intent'),
        sa.Column('satisfaction', sa.Float, nullable=True),
        sa.Column('iteration_count', sa.Integer, server_default='0'),
        sa.Column('intent_text', sa.Text, nullable=True),
        sa.Column('traditions', sa.JSON, nullable=True),
        sa.Column('final_scores', sa.JSON, nullable=True),
        sa.Column('user_feedback', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime, nullable=True),
    )
    op.create_index('idx_studio_sessions_user', 'studio_sessions', ['user_id'])
    op.create_index('idx_studio_sessions_state', 'studio_sessions', ['state'])
    op.create_index('idx_studio_sessions_created', 'studio_sessions', ['created_at'])

    # ── artifacts ──
    op.create_table(
        'artifacts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('studio_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('artifact_type', sa.String(20), nullable=False),
        sa.Column('file_path', sa.Text, nullable=True),
        sa.Column('analysis', sa.JSON, nullable=False),
        sa.Column('model_used', sa.String(100), nullable=True),
        sa.Column('analysis_cost_usd', sa.Float, server_default='0'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('idx_artifacts_session', 'artifacts', ['session_id'])
    op.create_index('idx_artifacts_type', 'artifacts', ['artifact_type'])

    # ── signals ──
    op.create_table(
        'signals',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('studio_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('timestamp', sa.DateTime, server_default=sa.func.now()),
        sa.Column('phase', sa.String(20), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('raw_data', sa.JSON, nullable=True),
        sa.Column('extracted_preferences', sa.JSON, nullable=True),
        sa.Column('brief_version', sa.Integer, nullable=True),
        sa.Column('time_spent_ms', sa.Integer, nullable=True),
    )
    op.create_index('idx_signals_session', 'signals', ['session_id'])
    op.create_index('idx_signals_timestamp', 'signals', ['timestamp'])
    op.create_index('idx_signals_action', 'signals', ['action'])

    # ── evolved_patterns ──
    op.create_table(
        'evolved_patterns',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('pattern_type', sa.String(50), nullable=False),
        sa.Column('pattern_key', sa.String(200), nullable=False),
        sa.Column('pattern_data', sa.JSON, nullable=False),
        sa.Column('confidence', sa.Float, server_default='0'),
        sa.Column('sample_count', sa.Integer, server_default='0'),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('idx_patterns_type_key', 'evolved_patterns', ['pattern_type', 'pattern_key'], unique=True)

    # ── brief_templates ──
    op.create_table(
        'brief_templates',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('template_brief', sa.JSON, nullable=False),
        sa.Column('source_session_count', sa.Integer, server_default='0'),
        sa.Column('avg_satisfaction', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    """Drop all Digestion V2 tables."""
    op.drop_table('brief_templates')
    op.drop_table('evolved_patterns')
    op.drop_table('signals')
    op.drop_table('artifacts')
    op.drop_table('studio_sessions')
