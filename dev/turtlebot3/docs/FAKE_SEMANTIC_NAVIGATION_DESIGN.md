# Fake Semantic Navigation — Design Specification

Minimal prototype: **user text command → keyword → object name → predefined goal pose → Nav2**. No YOLO, no LLM. Goal: connect language command + map-aware target selection + navigation.

---

## 1. Supported commands

- **`go to <object>`** — Navigate to the predefined safe pose for that object.  
  Examples: `go to table`, `go to chair`, `go to fridge`.
- **`navigate to <object>`** — Alias for `go to <object>`.

**Not supported in v1:** other verbs (e.g. “pick up”, “find”), multi-object, or negation. Invalid or unsupported commands are rejected (see §5).

---

## 2. Supported object labels

Initial set (extensible via config):

| Object  | Intended use        |
|---------|----------------------|
| `table` | Dining/desk table    |
| `chair` | Chair                |
| `fridge`| Kitchen fridge      |

Object names are **case-insensitive** after normalization (e.g. trim, lower). Add more labels in the semantic database (YAML) without code change.

---

## 3. Object → predefined safe pose (semantic database)

- **Storage:** One YAML file (e.g. `config/semantic_goals.yaml`) in the TurtleBot3/frontier workspace or a small shared package.
- **Format:** Each object has a **label** and a **goal pose** in the **map** frame (x, y, yaw or quaternion). Pose is “safe” in the sense of a hand-picked or pre-recorded navigation target (no detection).

Example:

```yaml
# semantic_goals.yaml (map frame)
semantic_goals:
  table:  { x: 2.0,  y: 1.0,  yaw: 0.0 }
  chair:  { x: -1.5, y: 0.5,  yaw: 1.57 }
  fridge: { x: 3.0,  y: -2.0, yaw: 3.14 }
```

- **Loading:** At startup, a single node loads this file and serves “object name → pose” for the supported map (or map_id) if you later support multiple maps.
- **No detection:** Poses are fixed for the map; no perception. “Fake” = we pretend the object is at that pose.

---

## 4. If the object is not yet “known” (region unknown in SLAM)

- **Definition of “unknown”:** We do **not** run object detection. For v1, “unknown” can mean either:
  - **Option A (simple):** Always treat configured objects as “known”; only check if the **goal pose is in currently free space** (e.g. costmap cost below threshold). If not (e.g. blocked), treat as unreachable.
  - **Option B (map coverage):** “Known” = goal pose lies in a **known** (free or occupied) cell in the current map; “unknown” = goal lies in **unknown** (-1) cell. If unknown → reject with reason “Object region not yet explored.”

**Recommendation for this week:** **Option B** — reject with a clear message: *“Object region not yet explored. Explore the map first.”* No waiting loop; user can retry after more exploration.

---

## 5. If the command is invalid

- **Unsupported command** (e.g. “pick up table”) → Reply: *“Unsupported command. Use: go to <object>.”*
- **Unknown object** (e.g. “go to sofa” not in semantic_goals) → Reply: *“Unknown object. Supported: table, chair, fridge.”*
- **Object not in semantic database** → Same as unknown object.
- **Goal pose in unknown/f blocked** (per §4) → Reply: *“Object region not yet explored.”* or *“Goal unreachable (blocked).”*

All replies are published on a **feedback/result topic** (e.g. `std_msgs/String` or a small custom message) so the UI or CLI can show them.

---

## 6. ROS2 node(s) to add

- **One node: `fake_semantic_cmd_node`** (or `semantic_goal_node`).
  - **Input:** User command (text) via **topic** (e.g. `user_command` `std_msgs/String`) or **service** (e.g. `NavigateToObject.srv` with `string object_name`).
  - **Behavior:**  
    - Parse command → extract verb + object.  
    - Look up object in semantic DB → get pose (map frame).  
    - Optional: check if pose is in known/free space (map/costmap).  
    - If valid: send **NavigateToPose** goal to Nav2; if invalid: publish or return error (see §5).
  - **Output:** Nav2 goal (existing action client); optional feedback topic.

**No new nodes for “object detection” or “language model”.** Optional: a tiny **keyword extractor** (e.g. regex or simple split) inside this node.

---

## 7. Topics / services / actions

| Type     | Name                 | Message / type           | Purpose |
|----------|----------------------|--------------------------|--------|
| Sub      | `user_command`       | `std_msgs/String`        | Raw text command (e.g. “go to table”). |
| Service  | `navigate_to_object` | `NavigateToObject.srv`   | Optional: `string object_name` → success + message. |
| Action   | `navigate_to_pose`   | Nav2 `NavigateToPose`    | Send goal to Nav2 (existing). |
| Pub      | `semantic_cmd_result`| `std_msgs/String`        | Feedback: “Navigating to table.” / “Unknown object.” / “Region not explored.” |

**Recommendation:** Start with **topic** `user_command` + **publisher** `semantic_cmd_result` to keep v1 minimal; add the service if you want request–response from a CLI or GUI.

---

## 8. Minimal flow (summary)

```text
User publishes "go to table" on user_command
  → Node parses "go to" + "table"
  → Lookup "table" in semantic_goals.yaml → (x, y, yaw)
  → (Optional) Check pose in map: known? free?
  → If invalid: publish error on semantic_cmd_result; stop
  → If valid: send NavigateToPose goal to Nav2; publish "Navigating to table." on semantic_cmd_result
```

---

## 9. File / package layout (suggestion)

- **Package:** Reuse or extend `tb3_frontier_exploration`, or add `tb3_fake_semantic_nav` (one node + config).
- **Config:** `config/semantic_goals.yaml` (object → pose); optionally `params.yaml` (topic names, frame_id, map/cost checks).
- **Launch:** `fake_semantic_nav.launch.py` — runs the node and loads semantic_goals; use with existing Nav2 + SLAM.

This design is enough to implement the pipeline this week and later swap in real object detection or LLM without changing the “object name → goal” and Nav2 interface.
