from GUI.Scenario.ScenarioEditor import ScenarioEditor

def launch_scenario_editor(self):
    """Launch the scenario editor"""
    try:
        self.scenario_editor = ScenarioEditor(self)
        self.scenario_editor.show()
    except Exception as e:
        print(f"Error launching scenario editor: {e}")