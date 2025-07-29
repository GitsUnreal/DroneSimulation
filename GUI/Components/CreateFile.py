def create_file_menu(main_window):
    """Create file menu with save/load and scenario editor options"""
    menubar = main_window.menuBar()
    file_menu = menubar.addMenu('File')
    
    # Scenario Editor
    scenario_action = file_menu.addAction('Scenario Editor')
    scenario_action.triggered.connect(main_window.launch_scenario_editor)
    
    file_menu.addSeparator()
    
    # Quick Save
    quick_save_action = file_menu.addAction('Quick Save')
    quick_save_action.setShortcut('F5')
    quick_save_action.triggered.connect(main_window.quick_save)
    
    # Quick Load
    quick_load_action = file_menu.addAction('Quick Load')
    quick_load_action.setShortcut('F9')
    quick_load_action.triggered.connect(main_window.quick_load)
    
    file_menu.addSeparator()
    
    # Save Simulation
    save_action = file_menu.addAction('Save Simulation')
    save_action.setShortcut('Ctrl+S')
    save_action.triggered.connect(main_window.save_simulation)
    
    # Load Simulation
    load_action = file_menu.addAction('Load Simulation')
    load_action.setShortcut('Ctrl+O')
    load_action.triggered.connect(main_window.load_simulation)