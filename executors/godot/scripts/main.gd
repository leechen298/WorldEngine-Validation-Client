extends Node2D

const CONTRACT_VERSION := "worldengine-godot-mvp-1"
const EXECUTOR_PRODUCER := "godot-executor"
const VIEWPORT_SIZE := Vector2(960, 540)
const AGENT_TEXTURE: Texture2D = preload("res://assets/agent.png")
const BEACON_TEXTURE: Texture2D = preload("res://assets/beacon.png")
const GROUND_TEXTURE: Texture2D = preload("res://assets/ground-tile.png")

var http: HTTPRequest
var status_label: Label
var telemetry_label: Label
var run_button: Button
var operation_sequence := 0
var challenge: Dictionary = {}
var scenario: Dictionary = {}
var operations: Dictionary = {}
var run_dir := ""
var base_url := ""
var session_id := ""
var projection: Dictionary = {}
var recent_event := "等待 WorldEngine"
var running := false
var auto_run := false
var challenge_path := ""


func _ready() -> void:
    get_viewport().size = VIEWPORT_SIZE
    http = HTTPRequest.new()
    http.timeout = 15.0
    add_child(http)
    _build_interface()
    _parse_arguments()
    queue_redraw()
    if challenge_path.is_empty():
        _set_status("未加载 challenge", "checker 尚未创建本次运行")
        return
    if not _load_contracts():
        return
    _set_status("challenge 已绑定", challenge.get("run_id", "unknown"))
    if auto_run:
        await get_tree().process_frame
        await _run_scenario()


func _build_interface() -> void:
    var layer := CanvasLayer.new()
    add_child(layer)

    var top_band := ColorRect.new()
    top_band.color = Color("#111b18")
    top_band.position = Vector2(0, 0)
    top_band.size = Vector2(960, 118)
    layer.add_child(top_band)

    var title := Label.new()
    title.text = "WorldEngine // 信号庭院"
    title.position = Vector2(28, 18)
    title.size = Vector2(600, 34)
    title.add_theme_font_size_override("font_size", 24)
    title.add_theme_color_override("font_color", Color("#f1ead8"))
    layer.add_child(title)

    status_label = Label.new()
    status_label.text = "准备中"
    status_label.position = Vector2(30, 55)
    status_label.size = Vector2(540, 24)
    status_label.add_theme_font_size_override("font_size", 15)
    status_label.add_theme_color_override("font_color", Color("#e2bd50"))
    layer.add_child(status_label)

    telemetry_label = Label.new()
    telemetry_label.text = "tick 0  |  revision 0  |  signal 0"
    telemetry_label.position = Vector2(30, 82)
    telemetry_label.size = Vector2(620, 22)
    telemetry_label.add_theme_font_size_override("font_size", 13)
    telemetry_label.add_theme_color_override("font_color", Color("#8eb7a2"))
    layer.add_child(telemetry_label)

    run_button = Button.new()
    run_button.text = "运行完整闭环"
    run_button.position = Vector2(744, 30)
    run_button.size = Vector2(184, 44)
    run_button.pressed.connect(_on_run_pressed)
    run_button.add_theme_font_size_override("font_size", 16)
    var button_style := StyleBoxFlat.new()
    button_style.bg_color = Color("#d9b84d")
    button_style.corner_radius_top_left = 4
    button_style.corner_radius_top_right = 4
    button_style.corner_radius_bottom_left = 4
    button_style.corner_radius_bottom_right = 4
    button_style.content_margin_left = 16
    button_style.content_margin_right = 16
    run_button.add_theme_stylebox_override("normal", button_style)
    run_button.add_theme_color_override("font_color", Color("#17231f"))
    layer.add_child(run_button)

    var event_band := ColorRect.new()
    event_band.color = Color("#17231f")
    event_band.position = Vector2(24, 476)
    event_band.size = Vector2(912, 44)
    layer.add_child(event_band)

    var event_label := Label.new()
    event_label.name = "EventLabel"
    event_label.text = recent_event
    event_label.position = Vector2(42, 486)
    event_label.size = Vector2(874, 24)
    event_label.add_theme_font_size_override("font_size", 13)
    event_label.add_theme_color_override("font_color", Color("#d9e2d6"))
    layer.add_child(event_label)


func _parse_arguments() -> void:
    var args := OS.get_cmdline_user_args()
    var index := 0
    while index < args.size():
        var argument: String = args[index]
        if argument == "--challenge" and index + 1 < args.size():
            challenge_path = args[index + 1]
            index += 2
        elif argument == "--auto-run":
            auto_run = true
            index += 1
        else:
            index += 1


func _load_contracts() -> bool:
    challenge = _read_json_file(challenge_path)
    if challenge.is_empty():
        _fail("challenge_invalid", "无法读取 challenge")
        return false
    if challenge.get("contract_version", "") != CONTRACT_VERSION:
        _fail("challenge_contract", "challenge contract 不匹配")
        return false
    run_dir = challenge_path.get_base_dir()
    base_url = str(challenge.get("worldengine_api_base", "")).trim_suffix("/")
    var project_dir := ProjectSettings.globalize_path("res://project.godot").get_base_dir()
    var scenario_path := project_dir.get_base_dir().get_base_dir().path_join(
        "contracts/mvp/scenario.json"
    )
    scenario = _read_json_file(scenario_path)
    if scenario.get("contract_version", "") != CONTRACT_VERSION:
        _fail("scenario_contract", "scenario contract 不匹配")
        return false
    DirAccess.make_dir_recursive_absolute(run_dir.path_join("executor/raw/responses"))
    DirAccess.make_dir_recursive_absolute(run_dir.path_join("executor/frames"))
    var operations_path := run_dir.path_join("executor/raw/operations.jsonl")
    if FileAccess.file_exists(operations_path):
        DirAccess.remove_absolute(operations_path)
    return true


func _on_run_pressed() -> void:
    if running or challenge_path.is_empty():
        return
    await _run_scenario()


func _run_scenario() -> void:
    running = true
    run_button.disabled = true
    _set_status("连接 WorldEngine", base_url)

    var capabilities := await _request_public(
        "capabilities",
        "capabilities.read",
        "GET",
        "/api/v1/capabilities"
    )
    if capabilities.is_empty():
        return
    if capabilities.get("contract_version", "") != scenario.get(
        "worldengine_contract_version", ""
    ):
        _fail("worldengine_contract", "WorldEngine contract 不匹配")
        return
    for item in capabilities.get("operations", []):
        operations[item.get("operation_id", "")] = item
    for required in scenario.get("required_operations", []):
        if not operations.has(required.get("operation_id", "")):
            _fail("capability_missing", str(required.get("operation_id", "")))
            return

    var variable: Dictionary = scenario.get("state_variable", {})
    var brief := {
        "seed": "godot-" + str(challenge.get("run_id", "")),
        "premise": "A public signal courtyard where one Agent responds to world state and feedback",
        "constraints": {
            "rendering_client": "godot",
            "authoritative_history": "worldengine"
        },
        "state_variables": [variable]
    }
    var package := await _call(
        "package_create",
        "world_packages.create",
        {
            "request_id": _request_id("package"),
            "brief": brief
        }
    )
    if package.is_empty():
        return
    var repeated_package := await _call(
        "package_repeat",
        "world_packages.create",
        {
            "request_id": _request_id("package-repeat"),
            "brief": brief
        }
    )
    if repeated_package.is_empty():
        return
    if package.get("package_hash", "") != repeated_package.get("package_hash", ""):
        _fail("package_determinism", "相同 brief 生成了不同 package hash")
        return

    var session := await _call(
        "session_create",
        "sessions.create",
        {
            "request_id": _request_id("session"),
            "package_id": package.get("package_id", ""),
            "package_hash": package.get("package_hash", "")
        }
    )
    if session.is_empty():
        return
    session_id = str(session.get("session_id", ""))
    projection = session.get("projection", {})
    _update_world("Session 已启动")
    _set_status("Session 已启动", session_id)
    await _capture_frame("initial.png")

    var window: Dictionary = projection.get("active_intervention_window", {})
    var accepted := await _call(
        "direction_accept",
        "directions.submit",
        {
            "request_id": _request_id("direction-accept"),
            "window_id": window.get("window_id", ""),
            "expected_revision": projection.get("revision", 0),
            "kind": "bounded_pressure",
            "target_ref": variable.get("key", "world_signal"),
            "summary": "Apply bounded pressure through the public intervention window",
            "magnitude": 1
        },
        {"session_id": session_id}
    )
    if accepted.is_empty():
        return
    var rejected := await _call(
        "direction_reject",
        "directions.submit",
        {
            "request_id": _request_id("direction-reject"),
            "window_id": window.get("window_id", ""),
            "expected_revision": projection.get("revision", 0),
            "kind": "direct_final_fact",
            "target_ref": variable.get("key", "world_signal"),
            "summary": "Attempt to overwrite the final canonical fact",
            "final_value": 10
        },
        {"session_id": session_id}
    )
    if rejected.is_empty():
        return

    var stepped := await _call(
        "step",
        "sessions.step",
        {
            "request_id": _request_id("step"),
            "step_count": scenario.get("initial_step_count", 2),
            "expected_revision": projection.get("revision", 0)
        },
        {"session_id": session_id}
    )
    if stepped.is_empty():
        return
    projection = stepped.get("projection", {})
    _update_world("方向已应用，Agent 完成两轮决策")
    _set_status("世界推进完成", "tick " + str(projection.get("tick", 0)))
    await _capture_frame("after-step.png")

    var action_id := ""
    var allowed_actions: Array = projection.get("allowed_actions", [])
    if not allowed_actions.is_empty():
        action_id = str(allowed_actions[0])
    var action := await _call(
        "action",
        "actions.submit",
        {
            "request_id": _request_id("action"),
            "expected_revision": projection.get("revision", 0),
            "action_id": action_id,
            "target_ref": variable.get("key", "world_signal"),
            "amount": 1
        },
        {"session_id": session_id}
    )
    if action.is_empty():
        return
    projection = action.get("projection", {})

    var feedback := await _call(
        "feedback",
        "feedback.submit",
        {
            "request_id": _request_id("feedback"),
            "expected_revision": projection.get("revision", 0),
            "feedback_type": "local_outcome_observed",
            "summary": "Godot observed the accepted public outcome",
            "related_event_ref": action.get("event_ref", "")
        },
        {"session_id": session_id}
    )
    if feedback.is_empty():
        return
    projection = feedback.get("projection", {})

    var post_step := await _call(
        "step_after_feedback",
        "sessions.step",
        {
            "request_id": _request_id("step-after-feedback"),
            "step_count": scenario.get("post_feedback_step_count", 1),
            "expected_revision": projection.get("revision", 0)
        },
        {"session_id": session_id}
    )
    if post_step.is_empty():
        return
    projection = post_step.get("projection", {})
    _update_world("反馈进入 Agent 下一轮决策")

    var events := await _call(
        "events",
        "events.poll",
        {},
        {"session_id": session_id},
        "?after_sequence=0&limit=200"
    )
    if events.is_empty():
        return
    var final_projection := await _call(
        "projection",
        "projection.read",
        {},
        {"session_id": session_id}
    )
    if final_projection.is_empty():
        return
    projection = final_projection
    var evidence := await _call(
        "evidence",
        "evidence.export",
        {},
        {"session_id": session_id}
    )
    if evidence.is_empty():
        return

    var event_items: Array = events.get("items", [])
    if not event_items.is_empty():
        recent_event = str(event_items[-1].get("event_type", "event"))
    _update_world("原始执行证据已保存")
    _set_status("执行完成，等待独立 checker", str(challenge.get("run_id", "")))
    await _capture_frame("final.png")
    _write_summary("completed", "", "")
    running = false
    if auto_run:
        get_tree().quit(0)
    else:
        run_button.disabled = true


func _call(
    label: String,
    operation_id: String,
    body: Dictionary,
    path_values: Dictionary = {},
    query: String = ""
) -> Dictionary:
    var operation: Dictionary = operations.get(operation_id, {})
    if operation.is_empty():
        _fail("operation_missing", operation_id)
        return {}
    var path := str(operation.get("path", ""))
    for key in path_values:
        path = path.replace("{" + str(key) + "}", str(path_values[key]))
    return await _request_public(
        label,
        operation_id,
        str(operation.get("method", "GET")),
        path + query,
        body
    )


func _request_public(
    label: String,
    operation_id: String,
    method: String,
    path: String,
    body: Dictionary = {}
) -> Dictionary:
    _set_status("执行 " + label, operation_id)
    var url := base_url + path
    var headers := PackedStringArray(["Accept: application/json"])
    var payload := ""
    var http_method := HTTPClient.METHOD_GET
    if method == "POST":
        http_method = HTTPClient.METHOD_POST
        headers.append("Content-Type: application/json")
        payload = JSON.stringify(body)
    var start_error := http.request(url, headers, http_method, payload)
    if start_error != OK:
        _fail("http_start", "无法启动 " + label)
        return {}
    var response: Array = await http.request_completed
    var result: int = response[0]
    var status_code: int = response[1]
    var response_body: PackedByteArray = response[3]
    operation_sequence += 1
    var response_relative := "executor/raw/responses/%03d-%s.json" % [
        operation_sequence,
        label
    ]
    var response_absolute := run_dir.path_join(response_relative)
    var response_file := FileAccess.open(response_absolute, FileAccess.WRITE)
    if response_file == null:
        _fail("response_write", "无法保存 " + label)
        return {}
    response_file.store_buffer(response_body)
    response_file.close()
    var context := HashingContext.new()
    context.start(HashingContext.HASH_SHA256)
    context.update(response_body)
    var response_hash := context.finish().hex_encode()
    _append_operation({
        "sequence": operation_sequence,
        "producer": EXECUTOR_PRODUCER,
        "label": label,
        "operation_id": operation_id,
        "method": method,
        "path": path,
        "request_id": body.get("request_id", null),
        "status_code": status_code,
        "transport_result": result,
        "response_file": response_relative,
        "response_sha256": response_hash,
        "recorded_at_epoch": Time.get_unix_time_from_system()
    })
    if result != HTTPRequest.RESULT_SUCCESS or status_code != 200:
        _fail("http_response", "%s 返回 HTTP %d" % [label, status_code])
        return {}
    var parsed = JSON.parse_string(response_body.get_string_from_utf8())
    if typeof(parsed) != TYPE_DICTIONARY:
        _fail("response_json", label + " 不是 JSON object")
        return {}
    if parsed.get("code", -1) != 0 or not parsed.has("data"):
        _fail("worldengine_response", label + " 返回业务错误")
        return {}
    return parsed.get("data", {})


func _append_operation(record: Dictionary) -> void:
    var path := run_dir.path_join("executor/raw/operations.jsonl")
    var file: FileAccess
    if FileAccess.file_exists(path):
        file = FileAccess.open(path, FileAccess.READ_WRITE)
        file.seek_end()
    else:
        file = FileAccess.open(path, FileAccess.WRITE)
    file.store_line(JSON.stringify(record))
    file.close()


func _capture_frame(name: String) -> void:
    queue_redraw()
    await get_tree().process_frame
    RenderingServer.force_draw(false)
    await get_tree().process_frame
    var image := get_viewport().get_texture().get_image()
    image.save_png(run_dir.path_join("executor/frames/" + name))


func _write_summary(outcome: String, error_code: String, detail: String) -> void:
    var value := {
        "contract_version": CONTRACT_VERSION,
        "producer": EXECUTOR_PRODUCER,
        "outcome": outcome,
        "run_id": challenge.get("run_id", ""),
        "nonce": challenge.get("nonce", ""),
        "session_id": session_id,
        "operation_count": operation_sequence,
        "frames": [
            "executor/frames/initial.png",
            "executor/frames/after-step.png",
            "executor/frames/final.png"
        ]
    }
    if not error_code.is_empty():
        value["error_code"] = error_code
        value["detail"] = detail
    var file := FileAccess.open(
        run_dir.path_join("executor/summary.json"),
        FileAccess.WRITE
    )
    file.store_string(JSON.stringify(value, "  ") + "\n")
    file.close()


func _read_json_file(path: String) -> Dictionary:
    if not FileAccess.file_exists(path):
        return {}
    var file := FileAccess.open(path, FileAccess.READ)
    var parsed = JSON.parse_string(file.get_as_text())
    file.close()
    if typeof(parsed) != TYPE_DICTIONARY:
        return {}
    return parsed


func _request_id(suffix: String) -> String:
    return str(challenge.get("run_id", "run")) + "-" + suffix


func _fail(code: String, detail: String) -> void:
    running = false
    run_button.disabled = challenge_path.is_empty()
    _set_status("执行中止", code + ": " + detail)
    if not run_dir.is_empty():
        _write_summary("error", code, detail)
    if auto_run:
        get_tree().quit(2)


func _set_status(primary: String, secondary: String) -> void:
    status_label.text = primary + "  //  " + secondary


func _update_world(event_text: String) -> void:
    recent_event = event_text
    var event_label := get_node_or_null("EventLabel")
    if event_label == null:
        event_label = get_tree().root.find_child("EventLabel", true, false)
    if event_label != null:
        event_label.text = recent_event
    var variables: Dictionary = projection.get("variables", {})
    var signal_value := int(variables.get("world_signal", 0))
    telemetry_label.text = "tick %s  |  revision %s  |  signal %+d  |  feedback %s" % [
        projection.get("tick", 0),
        projection.get("revision", 0),
        signal_value,
        projection.get("feedback_count", 0)
    ]
    queue_redraw()


func _draw() -> void:
    draw_rect(Rect2(0, 0, 960, 540), Color("#0e1513"))
    var world_rect := Rect2(24, 118, 912, 358)
    draw_rect(world_rect, Color("#29483a"))
    for x in range(32, 928, 32):
        for y in range(124, 476, 32):
            draw_texture_rect(
                GROUND_TEXTURE,
                Rect2(Vector2(x, y), Vector2(32, 32)),
                false
            )
    draw_rect(Rect2(64, 156, 832, 270), Color("#78a967"), false, 3.0)
    draw_rect(Rect2(84, 176, 300, 220), Color("#2b4b3a"))
    draw_rect(Rect2(104, 196, 260, 180), Color("#547c58"))
    draw_rect(Rect2(584, 174, 270, 224), Color("#315e59"))
    draw_rect(Rect2(604, 194, 230, 184), Color("#4d8e8a"))
    draw_texture_rect(BEACON_TEXTURE, Rect2(696, 250, 48, 64), false)

    var tick := int(projection.get("tick", 0))
    var agent_x: float = 210.0 + float(min(tick, 8)) * 34.0
    var agent_y := 294.0 + sin(float(tick)) * 10.0
    draw_texture_rect(
        AGENT_TEXTURE,
        Rect2(Vector2(agent_x, agent_y), Vector2(32, 40)),
        false
    )

    var signal_value := int(projection.get("variables", {}).get("world_signal", 0))
    var normalized: float = clampf((float(signal_value) + 20.0) / 40.0, 0.0, 1.0)
    draw_rect(Rect2(620, 346, 198, 12), Color("#17231f"))
    draw_rect(Rect2(622, 348, 194.0 * normalized, 8), Color("#e2bd50"))
    draw_circle(Vector2(720, 226), 42, Color(0.89, 0.74, 0.31, 0.12))
