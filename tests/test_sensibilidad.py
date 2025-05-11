import pandas as pd
from unittest.mock import MagicMock, patch
from fintualist.sensibilidad import SimuladorSensibilidad
from fintualist.escenarios import (
    ParametrosSimulacion,
)


def test_simulador_sensibilidad_init():
    """
    Prueba la inicialización de la clase SimuladorSensibilidad.
    Verifica que los atributos se inicialicen correctamente.
    """
    num_simulaciones = 100
    distribuciones_parametros = {"param1": MagicMock(), "param2": MagicMock()}
    simulador = SimuladorSensibilidad(num_simulaciones, distribuciones_parametros)

    assert simulador.num_simulaciones == num_simulaciones
    assert simulador.distribuciones_parametros == distribuciones_parametros
    assert isinstance(simulador.resultados_df, pd.DataFrame)


def test_simulador_sensibilidad_generar_parametros():
    """
    Prueba el método _generar_parametros de SimuladorSensibilidad.
    Verifica que se generen los parámetros correctamente, usando los
    valores por defecto de ParametrosSimulacion y los valores
    aleatorios de las distribuciones simuladas.
    """
    num_simulaciones = 2
    # Simulamos distribuciones que retornan valores predecibles para la prueba
    distribuciones_parametros = {
        "tasa_rentabilidad": MagicMock(rvs=lambda: 0.06),
        "precio_propiedad": MagicMock(rvs=lambda: 6000),
        "porcentaje_pie": MagicMock(rvs=lambda: 0.30),
        "tasa_hipotecaria": MagicMock(rvs=lambda: 0.04),
        "porcentaje_arriendo": MagicMock(rvs=lambda: 0.004),
        "tasa_plusvalia": MagicMock(rvs=lambda: 0.015),
        "porcentaje_remodelaciones": MagicMock(rvs=lambda: 0.006),
        "avaluo_exento": MagicMock(rvs=lambda: 1500),
        "avaluo_cambio_tramo": MagicMock(rvs=lambda: 5000),
        "tasa_contribuciones_tramo1": MagicMock(rvs=lambda: 0.01),
        "tasa_contribuciones_tramo2": MagicMock(rvs=lambda: 0.02),
    }
    simulador = SimuladorSensibilidad(num_simulaciones, distribuciones_parametros)
    parametros_generados = simulador._generar_parametros().model_dump()

    # Verificamos que los valores simulados se usen
    assert parametros_generados["tasa_rentabilidad"] == 0.06
    assert parametros_generados["precio_propiedad"] == 6000
    assert parametros_generados["porcentaje_pie"] == 0.30
    assert parametros_generados["tasa_hipotecaria"] == 0.04
    assert parametros_generados["porcentaje_arriendo"] == 0.004
    assert parametros_generados["tasa_plusvalia"] == 0.015
    assert parametros_generados["porcentaje_remodelaciones"] == 0.006
    assert parametros_generados["avaluo_exento"] == 1500
    assert parametros_generados["avaluo_cambio_tramo"] == 5000
    assert parametros_generados["tasa_contribuciones_tramo1"] == 0.01
    assert parametros_generados["tasa_contribuciones_tramo2"] == 0.02

    # Verificamos que los valores por defecto se utilicen si no hay distribución
    simulador = SimuladorSensibilidad(num_simulaciones, {})
    parametros_generados = simulador._generar_parametros().model_dump()
    assert (
        parametros_generados["anios"] == 25
    )  # Valor por defecto de ParametrosSimulacion
    assert parametros_generados["tasa_rentabilidad"] == 0.05


@patch("fintualist.sensibilidad.EscenarioArriendo", autospec=True)
@patch("fintualist.sensibilidad.EscenarioCompra", autospec=True)
def test_simulador_sensibilidad_ejecutar_simulacion(
    MockEscenarioCompra, MockEscenarioArriendo
):
    """
    Prueba el método ejecutar_simulacion de SimuladorSensibilidad usando patch.
    Verifica que se ejecuten las simulaciones correctamente y que los
    resultados se almacenen en el DataFrame.  Esta prueba aísla la lógica
    de SimuladorSensibilidad mockeando los objetos de escenario.
    """
    num_simulaciones = 3
    distribuciones_parametros = {"tasa_rentabilidad": MagicMock(rvs=lambda: 0.05)}

    # Configurar los mocks para que devuelvan resultados predecibles
    escenario_arriendo_mock = MockEscenarioArriendo.return_value
    escenario_arriendo_mock.calcular_capital_relativo_final.side_effect = [
        1000,
        1100,
        1200,
    ]
    escenario_compra_mock = MockEscenarioCompra.return_value
    escenario_compra_mock.calcular_capital_relativo_final.side_effect = [
        2000,
        2100,
        2200,
    ]

    # Mock de la generación de parámetros para que retorne valores controlados
    parametros_mock = ParametrosSimulacion(
        **{
            "anios": 25,
            "tasa_rentabilidad": 0.05,
            "precio_propiedad": 5000,
            "porcentaje_pie": 0.2,
            "tasa_hipotecaria": 0.034,
            "porcentaje_arriendo": 0.0038,
            "tasa_plusvalia": 0.012,
            "porcentaje_remodelaciones": 0.005,
            "avaluo_exento": 1256,
            "avaluo_cambio_tramo": 4424,
            "tasa_contribuciones_tramo1": 0.0093,
            "tasa_contribuciones_tramo2": 0.0109,
        }
    )

    simulador = SimuladorSensibilidad(num_simulaciones, distribuciones_parametros)
    simulador._generar_parametros = MagicMock(return_value=parametros_mock)

    simulador.ejecutar_simulacion()

    # Verificamos que los mocks de los escenarios se hayan instanciado correctamente
    assert MockEscenarioArriendo.call_count == num_simulaciones
    assert MockEscenarioCompra.call_count == num_simulaciones

    # Verificamos que los métodos de los escenarios se llamaron con los parámetros correctos
    escenario_arriendo_mock.calcular_capital_relativo_final.assert_called_with(
        parametros_mock
    )
    escenario_compra_mock.calcular_capital_relativo_final.assert_called_with(
        parametros_mock
    )

    # Verificamos que los resultados se almacenaron correctamente en el DataFrame
    assert len(simulador.resultados_df) == num_simulaciones
    assert (
        simulador.resultados_df["capital_relativo_arriendo"] == [1000, 1100, 1200]
    ).all()
    assert (
        simulador.resultados_df["capital_relativo_compra"] == [2000, 2100, 2200]
    ).all()
    for param, value in parametros_mock.model_dump().items():
        assert simulador.resultados_df.iloc[0][param] == value
