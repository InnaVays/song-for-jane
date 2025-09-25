from __future__ import annotations
from typing import List, Dict, Any, Optional, TypedDict
from pydantic import BaseModel, Field

# --- Optional Pydantic models (used by legacy code) ---
class Evidence(BaseModel):
    form_rules: Dict[str, Any] = Field(default_factory=dict)
    persona_cues: List[str] = Field(default_factory=list)
    positive_refs: List[str] = Field(default_factory=list)
    bans: List[str] = Field(default_factory=list)
    user_lexicon: List[str] = Field(default_factory=list)
    beat_hints: Dict[str, Dict[str, List[str]]] = Field(default_factory=dict)

class StyleRules(BaseModel):
    diction: List[str] = Field(default_factory=list)
    syntax: List[str] = Field(default_factory=list)
    imagery: List[str] = Field(default_factory=list)
    forbidden: List[str] = Field(default_factory=list)
    persona_markers: List[str] = Field(default_factory=list)
    meter_policy: Dict[str, Any] = Field(default_factory=dict)
    rhyme_policy: Dict[str, Any] = Field(default_factory=dict)

class Review(BaseModel):
    k: int
    issues: List[Dict[str, Any]] = Field(default_factory=list)
    patch: Optional[str] = None
    severity_max: str = "minor"

class FeedbackRecord(BaseModel):
    timestamp: Optional[str] = None
    like: List[str] = Field(default_factory=list)
    dislike: List[str] = Field(default_factory=list)
    targets: Dict[str, Any] = Field(default_factory=dict)
    examples: Dict[str, Any] = Field(default_factory=dict)

# --- Unified AppState used by both legacy and memory-fueled graphs ---
class AppState(TypedDict, total=False):
    # shared
    brief: Dict[str, Any]
    style: Dict[str, Any]
    stanzas: List[str]
    final_text: str
    preference_profile: Dict[str, Any]
    last_decision: str

    # legacy (plan-and-execute w/ critic)
    plan_variants: List[Dict[str, Any]]
    chosen_plan: Dict[str, Any]
    alts: List[Dict[str, Any]]
    selection_reason: str
    evidence: Dict[str, Any]
    reviews: List[Dict[str, Any]]
    version_log: List[Dict[str, Any]]

    # memory-fueled PaE (“branch the context, not the plan”)
    ready: bool
    global_pack: Dict[str, Any]
    plan: Dict[str, Any]
    toolcard: Dict[str, Any]
    retrieval_plan: Dict[str, Any]
    micro_pack: Dict[str, Any]
    chosen_context: str
    visible_stanza: Dict[str, Any]
    awaiting_feedback: bool
    raw_feedback: Any
    feedback_record: Dict[str, Any]
    _planner_cache: Dict[str, Any]
