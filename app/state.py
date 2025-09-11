from __future__ import annotations
from typing import List, Dict, Any, Optional, TypedDict
from pydantic import BaseModel, Field


class Evidence(BaseModel):
    form_rules: Dict[str, Any]
    persona_cues: List[str]
    positive_refs: List[str]
    bans: List[str]
    user_lexicon: List[str] = Field(default_factory=list)
    beat_hints: Dict[str, Dict[str, List[str]]] = Field(default_factory=dict)

class StyleRules(BaseModel):
    diction: List[str]
    syntax: List[str]
    imagery: List[str]
    forbidden: List[str]
    persona_markers: List[str]
    meter_policy: Dict[str, Any]
    rhyme_policy: Dict[str, Any]

class Review(BaseModel):
    k: int
    issues: List[Dict[str, Any]]
    patch: Optional[str] = None
    severity_max: str = "minor"

class FeedbackRecord(BaseModel):
    timestamp: str
    like: List[str] = Field(default_factory=list)
    dislike: List[str] = Field(default_factory=list)
    targets: Dict[str, Any] = Field(default_factory=dict)
    examples: Dict[str, Any] = Field(default_factory=dict)

class AppState(TypedDict, total=False):
    brief: Dict[str, Any]
    plan_variants: List[Dict[str, Any]]
    chosen_plan: Dict[str, Any]
    alts: List[Dict[str, Any]]
    selection_reason: str
    evidence: Dict[str, Any]
    style: Dict[str, Any]
    stanzas: List[str]
    reviews: List[Dict[str, Any]]
    final_text: str
    version_log: List[Dict[str, Any]]
    preference_profile: Dict[str, Any]
    last_decision: str