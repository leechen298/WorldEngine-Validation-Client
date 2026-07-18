extends SceneTree


func _initialize() -> void:
    var project_dir := ProjectSettings.globalize_path("res://project.godot").get_base_dir()
    var scenario_path := project_dir.get_base_dir().get_base_dir().path_join(
        "contracts/mvp/scenario.json"
    )
    if not FileAccess.file_exists(scenario_path):
        push_error("Missing shared MVP scenario contract")
        quit(1)
        return
    var scenario_file := FileAccess.open(scenario_path, FileAccess.READ)
    var scenario = JSON.parse_string(scenario_file.get_as_text())
    scenario_file.close()
    if typeof(scenario) != TYPE_DICTIONARY:
        push_error("Scenario contract is not a JSON object")
        quit(1)
        return
    if scenario.get("contract_version", "") != "worldengine-godot-mvp-1":
        push_error("Unexpected scenario contract version")
        quit(1)
        return
    if scenario.get("required_operations", []).size() != 13:
        push_error("Scenario operation catalog is incomplete")
        quit(1)
        return
    for asset in [
        "res://assets/agent.png",
        "res://assets/beacon.png",
        "res://assets/ground-tile.png"
    ]:
        if not FileAccess.file_exists(asset):
            push_error("Missing visual asset: " + asset)
            quit(1)
            return
    print("GODOT_MVP_CONTRACT_TEST_PASS")
    quit(0)
