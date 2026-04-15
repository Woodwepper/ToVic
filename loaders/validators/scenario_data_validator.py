from model.scenario.scenario import Scenario

class ScenarioDataValidator:
    """Esta clase valida los datos de un escenario para asegurarse de que sean correctos y completos antes de cargarlos en el juego"""

    def __init__(self, scenario_data: Scenario):
        self.scenario_data = scenario_data

    def validate(self) -> tuple[bool, list[str]]:
        errors = []

        # Validar que el escenario tenga un ID y un nombre
        if not self.scenario_data.id:
            errors.append("El escenario debe tener un ID")
        
        if not self.scenario_data.name:
            errors.append("El escenario debe tener un nombre")

        # Validar que el año sea un número entero positivo
        if not isinstance(self.scenario_data.year, int) or self.scenario_data.year <= 0:
            errors.append("El escenario debe tener un año válido (entero positivo)")

        # Validar que el escenario tenga al menos 2 paises
        if not isinstance(self.scenario_data.countries, list) or len(self.scenario_data.countries) < 2:
            errors.append("El escenario debe tener al menos 2 paises")

        # Validar que el escenario tenga al menos 2 provincias
        if not isinstance(self.scenario_data.provinces, list) or len(self.scenario_data.provinces) < 2:
            errors.append("El escenario debe tener al menos 2 provincias")

        # Validar que el escenario tenga al menos 1 ejército o este vacío (permitir escenarios sin ejércitos)
        if not isinstance(self.scenario_data.armies, list):
            errors.append("El escenario debe tener una lista de ejércitos (puede estar vacía)")

        # Validar que el escenario tenga al menos 1 casus belli
        if not isinstance(self.scenario_data.casus_belli, list) or len(self.scenario_data.casus_belli) < 1:
            errors.append("El escenario debe tener al menos 1 casus belli")

        # Validar que el escenario tenga

        