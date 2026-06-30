from typing import Any, Dict, List
from omniverobrix.core.state import AutonomyContext, AutonomyState, StepResult

class AutonomyLoop:
    def __init__(self, reasoner: Any, planner: Any, scheduler: Any, reflection_clusterer: Any, embedding_manager: Any = None, anomaly_detector: Any = None, chain_manager: Any = None, chain_synthesis_manager: Any = None, cockpit_bus: Any = None):
        self.reasoner = reasoner
        self.planner = planner
        self.scheduler = scheduler
        self.reflection_clusterer = reflection_clusterer
        self.embedding_manager = embedding_manager
        self.anomaly_detector = anomaly_detector
        self.chain_manager = chain_manager
        self.chain_synthesis_manager = chain_synthesis_manager
        self.cockpit_bus = cockpit_bus

    def observe(self, context: AutonomyContext) -> Dict[str, Any]:
        env_snap = context.environment.snapshot() if context.environment else None
        observation = {
            "mission": context.mission_state.snapshot(),
            "environment": env_snap,
            "memory": context.memory.snapshot(),
            "events": env_snap.events if env_snap else [],
        }

        if self.embedding_manager:
            self.embedding_manager.add(
                mission_id=context.mission_state.id,
                kind="observation",
                text=str(observation)
            )

        return observation

    def think(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return self.reasoner.generate_reflection(observation)
        except Exception as e:
            return {"error": str(e), "fallback": True}

    def plan(self, reflection: Dict[str, Any], context: AutonomyContext) -> List[Dict[str, Any]]:
        return self.planner.plan(reflection, context)

    def act(self, steps: List[Dict[str, Any]], context: AutonomyContext) -> List[StepResult]:
        results = []
        for step in steps:
            result = self.scheduler.execute(step, context)
            results.append(result)
        return results

    def reflect(self, observation: Dict[str, Any], actions: List[StepResult]) -> Dict[str, Any]:
        return self.reasoner.generate_post_action_reflection({
            "observation": observation,
            "actions": actions
        })

    def learn(self, reflection: Dict[str, Any], context: AutonomyContext):
        context.memory.store_reflection(reflection)
        context.memory.commit()

        if self.embedding_manager:
            self.embedding_manager.add(
                mission_id=context.mission_state.id,
                kind="reflection",
                text=str(reflection)
            )

        # clustering hook
        from omniverobrix.sovereign.reflection_clusterer import ReflectionRecord
        import time

        record = ReflectionRecord(
            id=reflection.get("id", "req-1"),
            mission_id=context.mission_state.id,
            timestamp=time.time(),
            phase="post_action",
            content=str(reflection),
            tags=[]
        )
        self.reflection_clusterer.add_reflection(record)
        
        if context.mission_state.is_at_cluster_checkpoint():
            self.reflection_clusterer.build_clusters(
                mission_id=context.mission_state.id
            )

    def check_stop(self, context: AutonomyContext, reflection: Dict[str, Any], anomalies: List[Any] = None) -> Any:
        from omniverobrix.sovereign.stop_conditions import StopConditionEngine
        stop_engine = StopConditionEngine(
            safety_rules=context.safety_rules,
            clusterer=self.reflection_clusterer,
            operator_channel=context.operator_channel
        )
        return stop_engine.evaluate(context, reflection)

    def run(self, context: AutonomyContext) -> AutonomyState:
        state, _ = self.run_with_chain(context)
        return state

    def run_with_chain(self, context: AutonomyContext) -> Any:
        import uuid
        cycle_id = str(uuid.uuid4())
        
        chain = None
        if self.chain_manager:
            chain = self.chain_manager.start_chain(context.mission_state.id, cycle_id)

        observation = self.observe(context)
        if chain: chain.add("observe", "captured environment + mission snapshot", {"observation": observation})

        reflection = self.think(observation)
        if chain: chain.add("think", "generated reflection", {"reflection": reflection})

        plan = self.plan(reflection, context)
        if chain: chain.add("plan", "generated plan", {"plan": plan})

        actions = self.act(plan, context)
        if chain: chain.add("act", "executed actions", {"actions": [a.__dict__ if hasattr(a, '__dict__') else a for a in actions]})

        post_reflection = self.reflect(observation, actions)
        if chain: chain.add("reflect", "post-action reflection", {"post_reflection": post_reflection})

        self.learn(post_reflection, context)
        if chain: chain.add("learn", "updated memory", {})

        clusters = self.reflection_clusterer.get_clusters(mission_id=context.mission_state.id)
        
        anomalies = []
        if self.anomaly_detector:
            anomalies = self.anomaly_detector.detect(
                context=context,
                observation=observation,
                reflection=post_reflection,
                clusters=clusters,
            )
            for a in anomalies:
                context.memory.store_reflection(a) # store anomalies in memory

        decision = self.check_stop(context, post_reflection, anomalies)
        
        if chain and self.chain_manager:
            self.chain_manager.persist(chain)

        if context.mission_state.is_complete() and self.chain_synthesis_manager:
            synthesis = self.chain_synthesis_manager.synthesize(context.mission_state.id)
            if hasattr(context.memory, "store_chain_synthesis"):
                context.memory.store_chain_synthesis(synthesis)

        if self.cockpit_bus:
            telemetry = {
                "cycle_id": cycle_id,
                "mission_id": context.mission_state.id,
                "phase": "complete",
                "observation": observation,
                "reflection": reflection,
                "plan": plan,
                "actions": [a.__dict__ if hasattr(a, '__dict__') else a for a in actions],
                "post_reflection": post_reflection,
                "anomalies": [a.__dict__ if hasattr(a, '__dict__') else a for a in anomalies],
                "stop_decision": decision.__dict__ if hasattr(decision, '__dict__') else decision,
                "reasoning_chain": [s.__dict__ if hasattr(s, '__dict__') else s for s in chain.steps] if chain else [],
                "environment": context.environment.snapshot().__dict__ if context.environment else None,
            }
            self.cockpit_bus.publish(telemetry)

        if decision.status != "continue":
            return AutonomyState(decision.status, {"reason": decision.reason, "details": decision.details}), chain

        return AutonomyState("running", post_reflection), chain
